# LogStreamX
Este repositório contém o programa LogStreamX, desenvolvido em linguagem Python, que tem por objetivo simular um sistema de login.

Nesse programa, podemos tambémm simular um ataque de fadiga MFA e efetuar a ingestão de logs em uma tabela personalizada do Log Analyticas, no ambiente do Microsoft Azure. 

Após a ingestão de logs, consultas KQL podem ser executadas nos dados da tabela personalizada.

O LogStreamX possui três módulos, que são:

### Autenticador

Nesse módulo, que simula uma página de login, é onde inserimos um nome de usuário e sua respectiva senha. 

Como em um cenário real, após inserirmos as credenciais do usuário, 
é enviado um código MFA de 3 números para o módulo celular. 

Ao enviar os 3 números, é informado qual dos 3 códigos é o correto, e que deverá ser selecionado no módulo celular, 
a fim de que se complete o processo de login. 

Ao inserir a senha errada uma determinada quantidade de vezes, o usuário é bloqueado. Para desbloqueá-lo, basta sair e entrar novamente no módulo. 

Possui também uma funcionalidade chamada “FICAR VULNERAVEL A MFA FATIGUE ATTACKS”, que como o nome diz, o torna susceptível a ataques dessa natureza. 

### Celular

Esse é o módulo que receberá os 3 códigos MFA que foram gerados e enviados pelo módulo autenticador. 

Além dos 3 números, aparecerá também as opções para negar ou ignorar a autorização. 

### Atacante

Esse módulo possui algumas funcionalidades utilizadas em ataques direcionados a credenciais de usuários. 

A primeira funcionalidade é a “BRUTE FORCE ATTACK”, que solicita um nome de usuário, 
e após a inserção, o módulo faz uma busca pelo usuário em um arquivo de senhas. Ao encontrar o usuário, testa todas as possibilidades programadas de senhas até encontrar a senha correta. 
Se não encontrar a senha, ele retorna um erro informando que não localizou a senha. Se encontrá-la, retorna a senha. 

A segunda funcionalidade é a “MFA FATIGUE ATTACK”, que solicita um nome de usuário e a senha, e logo após executa o ataque diretamente no modo autenticador, que por sua vez envia várias solicitações de autorização MFA ao módulo celular. 
Para essa funcionalidade funcionar, é necessário que o módulo autenticador esteja vulnerável a ataques de fadiga, o que é feito selecionando a segunda opção do menu no autenticador. 

A terceira funcionalidade, é uma automatização do ataque, que unifica a primeira e a segunda opção do menu. Nessa opção, é solicitado um nome de usuário, e o módulo já efetua automaticamente 
um ataque de brute force na senha e efetua também sem nenhuma interação adicional, um ataque de fadiga MFA. 
