# MODULO CELULAR
# DESENVOLVIDO EM PYTHON 3.10.9
#
# TRABALHO DE CONCLUSAO DE CURSO
# UNIVERSIDADE FEDERAL DE UBERLANDIA
# PÓS GRADUAÇÃO EM SEGURANÇA CIBERNÉTICA

import os, socket, hashlib, getpass
from threading import Thread

# armazena o endereço IP do autenticador e a porta
SERVER_HOST = '127.0.0.1' # ip do autenticador
SERVER_PORT = 12345 # porta do autenticador

# funçao que imprime o banner do modulo e o menu
def print_menu():

   os.system('cls')
   print('----------------------------------------------')
   print('| * * * * * * * * LOGSTREAMX * * * * * * * * |')
   print('----------------------------------------------')
   print('|               MÓDULO ATACANTE              |')
   print('----------------------------------------------')
   print('|   1. BRUTE FORCE ATTACK                    |')
   print('|   2. MFA FATIGUE ATTACK                    |')
   print('|   3. BRUTE FORCE COM MFA FATIGUE ATTACK    |')
   print('|   4. SAIR                                  |')
   print('----------------------------------------------')

# funçao auxiliar para descobrir a senha do arquivo de usuarios
# ela cria um hash md5 da senha digitada e retorna o hash
def md5hash(texto):
   m = hashlib.md5()
   m.update(texto.encode())
   return(m.hexdigest())

# funçao que executa o brute force para descobrir a senha de um usuario informado
def bruteforce(usuario):

   # Retorno 0 = Usuario nao encontrado
   # Retorno 1 = Senha nao encontrada
   # Retorno diferente de 0 e 1 = Retorna a senha encontrada

   # percorre o arquivo de senhas em busca do usuario
   # se encontrar o usuario, efetua o brute force
   with open('senhas.txt', 'r') as arquivo:
      for line in arquivo:
         usr_arquivo, senha = line.strip().split(':')
         if usuario == usr_arquivo:
            print(f'Executando brute force na senha do usuario {usuario}...')
            for i in range(0, 1000000):
               if md5hash(str(i)) == senha:
                  return i # retorna a senha encontrada, caso tiver encontrado
            return 1
            break # se o usuario for encontrado no arquivo, nao procurar mais
      return 0

# fica na escuta por mensagens de outros módulos
def escutaMSG():
   while True:
      try:
         message = s.recv(1024).decode() # recebe mensagens do autenticador
         print(message + '\n') # imprime a mensagem
      except ConnectionResetError:
           # se algum modulo se desconectar, nao fica mais na escuta por mensagens desse modulo
           break

def iniciar():   
 
   separador = "@" # usado para separar o nome do módulo da mensagem
   
   # define o nome que irá identificar esse modulo para o autenticador
   nome = 'ATACANTE'

   # envia o nome do modulo para o autenticador
   s.send(nome.encode())   

   # cria uma thread que fica na escuta por mensagens para esse módulo
   t = Thread(target=escutaMSG)
   # quando o modulo encerrar, a thread é encerrada
   t.daemon = True
   # inicia a thread
   t.start()
  
   # chama a funçao que imprime o menu na tela
   print_menu()

   opcaoInvalida = True
   sair = False

   # caso o usuario digite uma opção invalida, mostra um erro e solicita que digite uma opção válida
   while opcaoInvalida:
      while sair == False:
         opcao = input('\nEscolha uma opção: ')
         if opcao == '1':
            opcaoInvalida = False
            usuario = input('Digite o nome do usuario: ')
            result_bforce = bruteforce(usuario)
            if result_bforce == 0:
              print('Usuário não encontrado!')
            elif result_bforce == 1:
               print('Senha não encontrada!')  
            else:
               print(f'Senha encontrada: {result_bforce}')
            input('\nPressione qualquer tecla para voltar ao menu...')
            print_menu()

         elif opcao == '2':
            opcaoInvalida = False
            usuario = input('Digite o nome do usuario: ')
            senha = getpass.getpass('Digite a senha do usuario: ')
            print('EXECUTANDO FATIGUE ATTACK...')

            # cria uma lista com a opcao selecionada, o usuario, a senha e envia para o autenticador 
            lista = []
            lista.append(opcao)
            lista.append(usuario)
            lista.append(senha)
            to_send =  lista
            to_send = f'{nome}{separador}{to_send}'

            # envia a mensagem para o autenticador e retorna ao menu principal
            s.send(to_send.encode())
            input('\nPressione qualquer tecla para voltar ao menu...')
            print_menu()

         elif opcao == '3':
            opcaoInvalida = False
            usuario = input('Digite o nome do usuario: ')
            result_bforce = bruteforce(usuario)
            if result_bforce == 0:
              print('Usuário não encontrado!')
            elif result_bforce == 1:
               print('Senha não encontrada!')  
            else:
               print(f'Senha encontrada: {result_bforce}')
               print('EXECUTANDO FATIGUE ATTACK...')
               # cria uma lista com a opcao selecionada, nome e usuario e envia para o autenticador 
               lista = []
               lista.append(opcao)
               lista.append(usuario)
               lista.append(result_bforce)
               to_send =  lista
               to_send = f'{nome}{separador}{to_send}'

               # envia a mensagem para o autenticador e retorna ao menu principal
               s.send(to_send.encode())

            input('\nPressione qualquer tecla para voltar ao menu...')
            print_menu()

         elif opcao == '4':
            opcaoInvalida = False
            sair = True

         else:
            print('\nOpção invalida selecionada')
            input('\nPressione qualquer tecla para voltar ao menu...')
            print_menu()

if __name__ == "__main__":

   #limpa a tela
   os.system('cls')

   print('Iniciando módulo atacante...')

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
      print('\nConexão perdida com o módulo Autenticador!')
      print('\nPressione qualquer tecla para sair...')
      input()

   except KeyboardInterrupt:
      print('\n\nMódulo encerrado através do CTRL-C!')
      input()