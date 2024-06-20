Este é um bot feito para o servidor Brazil Progression Fantasy - um servidor com foco em histórias de fantasia.

O Bot atualmente contém a funcionalidade de criar, mostrar e gerenciar uma Tierlist (uma espécie de lista hierárquica, onde os usuários podem organizar suas histórias já lidas, de modo a mostrar para outros usuários suas preferências, criar debates e ver recomendações através das listas de outros usuários)

É um projeto que está em produção e sendo utilizado por pessoas reais. Foi utilizado conceitos de orientação a objeto, banco de dados (feito um CRUD com a ORM peewee), entre outros.

/tierlist show -> Mostra a tierlist do usuário que enviou o comando (parâmetro opcional: nome, que permite ver a tierlist de outra pessoa)
/tierlist add -> Adiciona um livro à um tier da lista
/tierlist del -> Remove um livro da lista do usuário
/tierlist swap -> Troca a posição de duas histórias, dentro do mesmo tier
E os comandos administrativos:
/admin admindel -> remove um livro do servidor, inclusive da lista dos usuários
/admin ban -> Torna um usuário impedido de utilizar qualquer comando da tierlist
/admin unban -> Remove o impedimento do comando acima.

Instalação:

Criar um bot em https://discord.com/developers e pegar o token

Após isso, importar python-dotenv: `pip install python-dotenv`

Uma vez instalado, criar um arquivo .dotenv na página inicial com a variável DISCORD_TOKEN que receberá o token do bot (utilizar aspas).

bot_token.py e adicionar a variável TOKEN, que recebe o token como string, assim: TOKEN = 'bot token'
