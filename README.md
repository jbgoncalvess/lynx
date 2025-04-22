# Lynx - Software de Gerenciamento de Servidores Web

O **Lynx** é um software web robusto e eficiente, projetado para monitorar, gerenciar e automatizar servidores web que utilizam o **Nginx** como balanceador de carga para containers de aplicação upstream. Esses containers são executados com tecnologia **LXC/LXD** e também utilizam **Nginx** para gerenciar as requisições localmente. Desenvolvido com **Django** e **MDBootstrap**, o Lynx oferece uma interface moderna, responsiva e amigável, proporcionando controle completo sobre o ambiente de balanceamento e containers.

---

## Principais Funcionalidades

### Monitoramento de Servidores e Containers
- **Desempenho do Servidor Host:**
  - Registro diário de valores máximos e mínimos de containers ativos nos últimos 7 dias.
  - Monitoramento em tempo real do número de conexões ativas e Requisições por Segundo (**RPS**), com histórico visual.
  
- **Métricas de Containers:**
  - Acompanhamento do uso de **CPU**, **memória**, **disco**, tempo de uptime e número de processos ativos.
  - Gráficos dinâmicos e interativos atualizados automaticamente a cada 10 segundos.

---

### Gerenciamento de Containers
- Controle completo dos containers upstream:
  - **Ações manuais:** iniciar, pausar e reiniciar containers.
  - Configuração de endereços IPv4 e gerenciamento de IPv6.
  - Detalhamento do status de execução, nome e IPs atribuídos.
- Ajuste dinâmico da rede para atender às necessidades do servidor.

---

### Automação e Balanceamento de Carga
- **Configuração Automática do Nginx:**
  - Atualização em tempo real do arquivo de configuração do Nginx.
  - Containers em execução (**RUNNING**) são adicionados automaticamente ao balanceador de carga.
  - Containers pausados ou inativos (**STOPPED**) são removidos do upstream, garantindo um balanceamento eficiente e sem intervenção manual.

- **Gerenciamento de Recursos:**
  - Inicialização e interrupção automáticas de containers com base no uso médio de CPU, otimizando o consumo de recursos do servidor.

---

### Gestão de Imagens
- **Listagem de Imagens Disponíveis:**
  - Exibição detalhada de nome, arquitetura, descrição, tamanho e data de upload.
- **Manutenção:** Exclusão de imagens desnecessárias para otimizar o armazenamento.

---

## Tecnologias Utilizadas

### No Lynx
- **Python:** Base do backend, oferecendo automação e integração segura.
- **Django:** Framework web para gerenciamento das rotas, lógica do servidor e banco de dados.
- **HTML e CSS:** Estruturação e estilização das páginas, com foco em responsividade e usabilidade.
- **JavaScript:** Elementos dinâmicos do frontend, como gráficos e atualizações automáticas.
- **MDBootstrap:** Biblioteca para estilização moderna e responsiva.

### No Servidor Monitorado
- **Nginx:** Balanceador de carga e servidor web, essencial para distribuir requisições entre os containers upstream.
- **LXC/LXD:** Tecnologia de virtualização para containers, garantindo isolamento e flexibilidade.

---

## Bibliotecas-Chave

- **Paramiko:** Gerenciamento seguro de conexões **SSH**, permitindo ao Lynx operar remotamente.
- **Subprocess:** Execução de comandos no sistema operacional para gerenciamento de containers e reconfiguração do Nginx.

---

## Arquitetura e Diferenciais

O **Lynx** foi projetado para operar remotamente, sem a necessidade de instalação no mesmo servidor que está sendo monitorado. Ele utiliza conexões **SSH** seguras para comunicação, coleta de métricas e execução de comandos.

### Estrutura do Servidor Monitorado:
- **Usuário SSH Configurado:** Um usuário chamado **lynx** deve ser preparado para conexão segura.
- **Serviço lynx.service:** Serviço customizado em **Python 3**, responsável por enviar métricas e executar comandos necessários.

---

O **Lynx** combina automação, monitoramento avançado e gerenciamento intuitivo, sendo ideal para servidores web que utilizam **Nginx** como balanceador de carga e **LXC/LXD** para containers de aplicação.
