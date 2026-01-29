# MODULO CELULAR
# DESENVOLVIDO EM PYTHON 3.10.9
#
# TRABALHO DE CONCLUSAO DE CURSO
# UNIVERSIDADE FEDERAL DE UBERLANDIA
# PÓS GRADUAÇÃO EM SEGURANÇA CIBERNÉTICA

import os, socket
from threading import Thread

# armazena o endereço IP do autenticador e a porta
SERVER_HOST = '127.0.0.1' # ip do autenticador
SERVER_PORT = 12345 # porta do autenticador

# funçao que imprime o banner do modulo
def print_banner():

   os.system('cls')
   print('------------------------------------')
   print('| * * * * * LOGSTREAMX * * * * * * |')
   print('------------------------------------')
   print('|          MÓDULO CELULAR          |')
   print('------------------------------------')
   print('\nAguardando códigos MFA...\n')

#desativa o envio de mensagens, ativando apenas quando receber os códigos MFA do autenticador
enviomsg = False   

# fica na escuta por mensagens de outros módulos
def escutaMSG():
   global enviomsg
   while True:
      try:
         message = s.recv(1024).decode() # recebe mensagens do autenticador
         print(message) # imprime a mensagem      
         enviomsg = True
      except ConnectionResetError:
           # se algum modulo se desconectar, nao fica mais na escuta por mensagens desse modulo
           break

def iniciar():

   separador = "@" # usado para separar o nome do módulo da mensagem

   # identifica-se para o modulo autenticador
   nome = 'CELULAR'

   # envia o nome do modulo para o autenticador
   s.send(nome.encode())

   # cria uma thread que fica na escuta por mensagens para esse módulo
   t = Thread(target=escutaMSG)
   # quando o modulo encerrar, a thread é encerrada
   t.daemon = True
   # inicia a thread
   t.start()

   # chama a funçao que imprime o banner do modulo na tela
   print_banner()

   global enviomsg

   while True:   
      # assim que receber os códigos MFA do autenticador, já fica habilitado para o envio de mensagens para o autenticador
      # que nesse caso seria o codigo MFA
      if enviomsg == True:
         # nessa variavel é onde fica armazenada a msg que vamos enviar para o autenticador
         msg_a_enviar =  input()      
         # só permite enviar para o autenticador mensagens esperadas, ou seja, somente numeros
         # ou as opções I(gnorar) ou N(negar)
         # se for uma resposta MFA válida, envia a mensagem e retorna ao inicio, esperando por novos códigos MFA
         if (msg_a_enviar.isdigit() == True or msg_a_enviar.upper() == 'I' or msg_a_enviar.upper() == 'N'):
            msg_a_enviar = f"{nome}{separador}{msg_a_enviar}" 
            s.send(msg_a_enviar.encode())
         input('\nPressione qualquer tecla para voltar ao inicio...')
         print_banner()
         # após enviar o numero ou codigo para o autenticador, desativa o envio de mensagens
         enviomsg = False

if __name__ == "__main__":

   #limpa a tela
   os.system('cls')

   print('Iniciando módulo celular...')

   # inicializa o socket TCP, fazendo o tratamento de alguns erros comuns
   try:
      s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      # conecta no servidor (autenticador)
      s.connect((SERVER_HOST, SERVER_PORT))
      iniciar()

   except ConnectionRefusedError:
      print('\nMódulo Autenticador não inicializado!')
      print('\nPressione qualquer tecla para sair...')
      input()

   except ConnectionResetError:
      print('Conexão perdida com o módulo Autenticador!')
      print('\nPressione qualquer tecla para sair...')
      input()

   except KeyboardInterrupt:
      print('\n\nMódulo encerrado através do CTRL-C!')
      input()