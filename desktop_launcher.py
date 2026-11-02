import getpass
import os
import secrets
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path


def application_directory():
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA")
        if not root:
            raise RuntimeError("Não foi possível localizar a pasta local de dados do Windows.")
        return Path(root) / "ConsentLedger"
    root = os.environ.get("XDG_DATA_HOME")
    return Path(root) / "consent-ledger" if root else Path.home() / ".local" / "share" / "consent-ledger"


def create_first_operator():
    from django.contrib.auth import get_user_model
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError

    user_model = get_user_model()
    if user_model.objects.exists():
        return

    print("\nPrimeira execução: crie a conta administradora local.")
    username = input("Usuário: ").strip()
    if not username:
        raise RuntimeError("O nome de usuário não pode ficar vazio.")
    email = input("E-mail (opcional): ").strip()

    while True:
        password = getpass.getpass("Senha (mínimo 14 caracteres): ")
        confirmation = getpass.getpass("Confirme a senha: ")
        if password != confirmation:
            print("As senhas não conferem. Tente novamente.")
            continue
        try:
            validate_password(password, user_model(username=username, email=email))
        except ValidationError as error:
            print("Senha recusada: " + "; ".join(error.messages))
            continue
        break

    user_model.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
    print("Conta administradora criada.")


def open_browser(url):
    time.sleep(1.0)
    webbrowser.open(url, new=2)


def main():
    self_test = sys.argv[1:] == ["--self-test"]
    data_directory = application_directory()
    data_directory.mkdir(parents=True, exist_ok=True)

    secret_path = data_directory / "secret.key"
    if not secret_path.exists():
        secret_path.write_text(secrets.token_urlsafe(64), encoding="utf-8")
    secret_key = secret_path.read_text(encoding="utf-8").strip()
    if len(secret_key) < 50:
        raise RuntimeError(f"A chave local está inválida. Apague somente {secret_path} e reinicie.")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ["SECRET_KEY"] = secret_key
    os.environ["DEBUG"] = "False"
    os.environ["ALLOWED_HOSTS"] = "127.0.0.1,localhost"
    os.environ["CSRF_TRUSTED_ORIGINS"] = "http://127.0.0.1,http://localhost"
    os.environ["SECURE_SSL_REDIRECT"] = "False"
    os.environ["SESSION_COOKIE_SECURE"] = "False"
    os.environ["CSRF_COOKIE_SECURE"] = "False"
    os.environ["DATABASE_PATH"] = str(data_directory / "consent-ledger.sqlite3")

    import django
    from django.core.management import call_command
    from waitress import create_server

    django.setup()
    call_command("migrate", interactive=False, verbosity=0)

    if self_test:
        from django.test import Client

        client = Client()
        health = client.get("/healthz", HTTP_HOST="127.0.0.1")
        admin = client.get("/admin/", HTTP_HOST="127.0.0.1")
        if health.status_code != 200 or health.json() != {"status": "ok"}:
            raise RuntimeError("O endpoint de saúde não passou na verificação empacotada.")
        if admin.status_code != 302 or "/admin/login/" not in admin["Location"]:
            raise RuntimeError("A autenticação administrativa não passou na verificação empacotada.")
        print("Verificação do executável concluída: migração, saúde e autenticação OK.")
        return

    create_first_operator()

    from config.wsgi import application

    server = create_server(application, host="127.0.0.1", port=0)
    url = f"http://127.0.0.1:{server.effective_port}/admin/"

    print("\nConsent Ledger está disponível somente neste computador.")
    print(f"Painel: {url}")
    print(f"Dados locais: {data_directory}")
    print("Mantenha esta janela aberta. Pressione Ctrl+C para encerrar.")
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    try:
        server.run()
    except KeyboardInterrupt:
        print("\nConsent Ledger encerrado.")
    finally:
        server.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nNão foi possível iniciar o Consent Ledger: {error}", file=sys.stderr)
        raise
