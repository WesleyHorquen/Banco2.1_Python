import textwrap
from abc import ABC, abstractmethod
from datetime import datetime

def menu():
    print('\n----------> Bem vindo ao WHS.Bank <----------')
    menu = '''
    Menu:
    [1] -\tDepositar
    [2] -\tSacar
    [3] -\tExtrato
    [7] -\tNovo Usuário
    [8] -\tNova Conta
    [9] -\tListar Contas
    [0] -\tSair
    =>> '''
    return input(textwrap.dedent(menu))

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
    
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)
    @property
    def saldo(self):
        return self._saldo
    @property
    def numero(self):
        return self._numero
    @property
    def agencia(self):
        return self._agencia
    @property
    def cliente(self):
        return self._cliente
    @property
    def historico(self):
        return self._historico
    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo
        if excedeu_saldo:
            print('\nOperação falhou! Você não tem saldo suficiente!')
        elif valor > 0:
            self._saldo -= valor
            print('\nSaque realizado com sucesso!')
            return True
        else:
            print('\nOperação falhou! O valor informado é inválido.')
            return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print('\nDeposito realizado com sucesso!')
        else:
            print('\nOperação falhou! O valo informado é inválido.')
            return False
        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao['Tipo'] == Saque.__name__])
        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print('\nOperação falhou! O valor do saque excede o limite.')
        elif excedeu_saques:
            print('\nOperação falhou! Número máximo de saques excedido.')
        else:
            return super().sacar(valor)
        return False
    
    def __str__(self):
        return f'''\
                Agência:\t{self.agencia}
                C/C:\t\t{self.agencia}
                Titular:\t{self.cliente.nome}
            '''

class Historico:
    def __init__(self):
        self._transacoes = []
    @property
    def transacoes(self):
        return self._transacoes
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                'Tipo': transacao.__class__.__name__,
                'Valor': transacao.valor,
                'Data': datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            }
        )


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    @property
    def valor(self):
        return self._valor
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def depositar(clientes):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado.')
        return
    
    valor = float(input('Informe o valor do depósito: R$ '))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input('Infore o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado!')
        return
    valor = int(input('Digite o valor a ser sacado: R$ '))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado.')
        return
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    print('=========== EXTRATO ===========')
    transacoes = conta.historico.transacoes

    extrato = ''
    if not transacoes:
        extrato = 'Não foram realizadas transações.'
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['Tipo']}:\n\tR$ {transacao['Valor']:.2f}"
    print(extrato)
    print(f'\nSaldo:\n\tR$ {conta.saldo:.2f}')
    print('=' * 31)

def criar_cliente(clientes):
    cpf = input('Informe o CPF: ')
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print('\nJá existe um cliente com esse CPF.')
        return
    nome = input('Informe o nome completo: ')
    data_nascimento = input('Informe a data de nascimento (dd-mm-aaaa): ')
    endereco = input('Informe o endereço (logradouro, nro, bairro - cidade / sigla do estado): ')

    cliente = PessoaFisica(nome=nome,
                           data_nascimento=data_nascimento,
                           cpf=cpf,
                           endereco=endereco)
    
    clientes.append(cliente)

    print('\nCliente cadastrado com sucesso!')

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print('Cliente não possui conta!')
        return
    return cliente.contas[0]

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe os números de seu CPF: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('\nCliente não encontrado, fluxo de criação de conta encerrado!')
        return
    conta = ContaCorrente.nova_conta(cliente=cliente,
    numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print('\nConta criada com sucesso!')

def listar_contas(contas):
    for conta in contas:
        print('=' * 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == '1':
            depositar(clientes)
        elif opcao == '2':
            sacar(clientes)
        elif opcao == '3':
            exibir_extrato(clientes)
        elif opcao == '7':
            criar_cliente(clientes)
        elif opcao == '8':
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
        elif opcao == '9':
            listar_contas(contas)
        elif opcao == '0':
            break
        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")

main()
    
