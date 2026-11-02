# Consent Ledger

Registro auto-hospedado de consentimentos e descadastros para pequenos negócios. A interface administrativa permite manter contatos, documentar a origem/evidência de cada solicitação e consultar o evento mais recente.

**Este MVP não envia mensagens, não importa listas de terceiros e não automatiza contas pessoais.** Ele não comprova que a evidência informada é verdadeira e não substitui aconselhamento jurídico nem uma avaliação de conformidade com a LGPD ou com as políticas da plataforma de mensagens.

Esta versão é um protótipo para avaliação, não um produto pronto para dados reais de clientes. O banco SQLite não oferece criptografia de campos pela aplicação; antes de uso comercial, faça revisão independente, proteja o armazenamento e os backups e estabeleça processo de retenção/exclusão.

## Aplicativo executável para Windows

O executável desktop inicia o painel local no navegador e aceita conexões **somente do próprio computador**. Ele não expõe o banco na internet. Na primeira abertura, crie o operador na janela de console. Banco e chave ficam em `%LOCALAPPDATA%\ConsentLedger`; faça uma cópia segura da pasta para preservar os registros e a chave. Não compartilhe essa pasta nem use dados reais de clientes antes de uma revisão de segurança.

Para criar `dist\ConsentLedger.exe` em Windows x64 com Python 3.12:

```powershell
.\build-windows.ps1
```

Inicie `dist\ConsentLedger.exe` e mantenha a janela aberta enquanto usa o painel. Para encerrar, pressione `Ctrl+C` nessa janela. Este binário desktop é independente da VPS/Hostinger; o botão Hostinger é para a implantação Docker Compose documentada abaixo.

## Recursos do MVP

- Contatos identificados por telefone no formato internacional E.164.
- Eventos de consentimento e descadastro com origem, evidência, data e operador.
- Histórico de eventos somente de acréscimo pela aplicação; correções devem ser registradas como um novo evento.
- Painel administrativo com autenticação, proteção CSRF, bloqueio temporário após tentativas de login e permissões do Django.
- Banco SQLite persistido em volume Docker e endpoint de saúde sem dados pessoais.

## Executar localmente

Requer Python 3.12 ou Docker Compose.

```powershell
Copy-Item .env.example .env
```

Edite `.env`: defina um `SECRET_KEY` aleatório, `DEBUG=False`, os hosts/origens corretos e mantenha cookies seguros quando houver HTTPS. Para gerar uma chave local:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Com Docker:

```powershell
docker compose up --build -d
docker compose exec app python manage.py createsuperuser
```

Abra `http://localhost:8000/admin/` apenas em ambiente local. Em produção, configure domínio, proxy reverso e HTTPS antes de habilitar o serviço; mantenha a porta do container acessível somente pelo proxy. Use `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` com seus domínios reais.

Sem Docker, crie um ambiente virtual, instale `requirements.txt`, configure as variáveis de `.env` no ambiente do processo, execute `python manage.py migrate`, `python manage.py createsuperuser` e `python manage.py runserver` apenas para desenvolvimento.

## Implantação em VPS

O `compose.yaml` foi preparado para implantação em uma VPS Docker Compose. O volume `ledger_data` guarda o banco; faça backups criptografados e teste a restauração. Não exponha a porta diretamente à internet. Não use `DEBUG=True`, senhas padrão ou um `SECRET_KEY` compartilhado. O deploy não inclui domínio, VPS, backups externos, monitoramento ou configuração de TLS.

Para o botão do programa Hostinger, primeiro obtenha um código de parceiro e substitua o marcador abaixo pelo código fornecido no painel:

```markdown
[![Deploy on Hostinger](https://assets.hostinger.com/vps/deploy.svg)](https://www.hostinger.com/deploy?template=CONCIERGE-WEB/consent-ledger&ref=YOUR_PARTNER_CODE)
```

O projeto ainda não foi aprovado no programa; o link acima é apenas o formato documentado pela Hostinger, não um link de indicação ativo.

## Segurança e privacidade

- Não há envio de mensagens nem armazenamento de tokens de API.
- Os dados ficam no servidor que você administra; quem implanta é responsável por acesso, backups, retenção e solicitações de titulares.
- O SQLite armazena os campos de contato e evidência sem criptografia no nível da aplicação; use proteção de disco/volume e backups criptografados e não trate isso como adequado para produção sem revisão.
- Crie contas de operador individuais e use senhas fortes; não compartilhe credenciais.
- O log é append-only na interface e na camada de modelo, mas não é um mecanismo inviolável contra administradores do banco/servidor.
- Faça revisão de segurança e validação jurídica antes de uso comercial ou de armazenar dados reais.

## Licença

MIT. Este projeto é independente e não incorpora código, imagens ou fluxos dos materiais inspecionados.
