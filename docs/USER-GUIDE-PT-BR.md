# MIDI Captain MAX - Guia do Usuário do Editor de Configuração

**Versão:** 1.0  
**Idioma:** Português (Brasil)

---

## Índice

1. [Introdução](#introdução)
2. [Primeiros Passos](#primeiros-passos)
3. [Interface Principal](#interface-principal)
4. [Configurações do Dispositivo](#configurações-do-dispositivo)
5. [Sistema de Bancos/Páginas](#sistema-de-bancospáginas)
6. [Configuração de Botões](#configuração-de-botões)
7. [Perfis de Dispositivos](#perfis-de-dispositivos)
8. [Ações Condicionais](#ações-condicionais)
9. [Botões Multi-Estado (Keytimes)](#botões-multi-estado-keytimes)
10. [Configuração do Encoder](#configuração-do-encoder)
11. [Pedais de Expressão](#pedais-de-expressão)
12. [Configurações de Display](#configurações-de-display)
13. [Monitor MIDI](#monitor-midi)
14. [Atalhos de Teclado](#atalhos-de-teclado)
15. [Dicas e Melhores Práticas](#dicas-e-melhores-práticas)
16. [Solução de Problemas](#solução-de-problemas)

---

## Introdução

O **Editor de Configuração MIDI Captain MAX** é uma aplicação desktop que permite personalizar seu controlador de pedal Paint Audio MIDI Captain (modelos STD10 ou Mini6). Com este editor, você pode:

- Configurar rótulos, cores e comandos MIDI dos botões
- Configurar ações complexas com múltiplos comandos
- Usar perfis de dispositivos para equipamentos populares (Quad Cortex, Helix, Kemper, etc.)
- Criar lógica condicional para comportamento de botões sensível ao contexto
- Configurar encoders e pedais de expressão
- Personalizar o display do dispositivo
- Depurar tráfego MIDI com o Monitor MIDI integrado
- Trabalhar em modo de desenvolvimento ou performance

---

## Primeiros Passos

### Conectando Seu Dispositivo

1. **Conecte** seu MIDI Captain ao computador via USB
2. **Habilite o Modo USB Drive** (se não estiver em modo dev):
   - Desligue o dispositivo
   - Segure o **Switch 1** (botão superior esquerdo)
   - Ligue mantendo o Switch 1 pressionado
   - Solte quando o drive USB aparecer
3. O editor detectará automaticamente seu dispositivo

### Primeiro Uso

Quando você abrir o editor:

1. Seu(s) dispositivo(s) conectado(s) aparecerá(ão) no **menu suspenso** no topo
2. Selecione seu dispositivo para carregar a configuração atual
3. O layout do dispositivo aparecerá mostrando todos os botões
4. Quaisquer alterações não salvas serão marcadas com um indicador de ponto amarelo

---

## Interface Principal

O editor é dividido em três áreas principais:

### Painel Esquerdo - Visão Geral do Dispositivo

- **Layout do Dispositivo**: Representação visual interativa do seu controlador de pedal
  - Clique em qualquer botão para selecioná-lo para edição
  - Cores e rótulos dos botões refletem a configuração atual
  - Botões com múltiplos comandos mostram indicadores de badge
  - Pré-visualização de LED mostra a aparência do botão
- **Grade de Dispositivo** (visualização opcional): Visualização em lista de todos os botões
- **Barra de Status**: Mostra status de salvamento e erros de validação

### Painel Central - Configurações do Botão

Configuração detalhada para o botão selecionado:

- **ID e Rótulo do Botão**: Identifique e nomeie seu botão
- **Cor**: Escolha a cor do LED da paleta predefinida
- **Comportamento**: Configure modo e configurações de canal
- **Ações**: Configure comandos MIDI para diferentes eventos
- **Substituições de Estado**: Configure comportamento multi-estado (keytimes)
- **Configurações Avançadas**: Grupos de seleção, modo off, brilho reduzido

### Lado Direito - Configurações Globais

- Tipo de dispositivo e configurações gerais
- Nome do drive USB
- Alternância do modo de desenvolvimento
- Configurações de tamanho de texto do display

### Barra de Ferramentas

- **Desfazer/Refazer**: Navegue pelo histórico de configuração (⌘Z / ⌘⇧Z)
- **Ver JSON**: Inspecione a configuração bruta
- **Salvar**: Grave alterações no dispositivo (⌘S)
- **Recarregar**: Descarte alterações e recarregue do dispositivo
- **Resetar**: Restaure a configuração padrão de fábrica

---

## Configurações do Dispositivo

### Tipo de Dispositivo

Selecione seu modelo de hardware:
- **STD10**: Controlador de pedal com 10 botões e encoder
- **Mini6**: Controlador compacto com 6 botões

### Canal MIDI Global

Canal MIDI padrão para todos os botões (1-16). Botões individuais podem sobrescrever isso.

### Nome do Drive USB

Personalize o nome do volume quando o modo USB drive estiver habilitado:
- Máximo de 11 caracteres
- Apenas letras, números e underscores
- Convertido automaticamente para maiúsculas

**Exemplo**: `MIDICAPTAIN`, `MEUCONTROL`, `PEDAL_01`

### Modo de Desenvolvimento

- **DESLIGADO** (Modo Performance): Drive USB oculto por padrão. Segure Switch 1 durante o boot para habilitar temporariamente.
- **LIGADO** (Modo Dev): Drive USB sempre monta automaticamente. Útil durante configuração, mas pode impactar tempo de boot.

---

## Sistema de Bancos/Páginas

O **Sistema de Bancos/Páginas** permite armazenar até 8 configurações completas de botões e alternar entre elas instantaneamente no seu dispositivo. Isso é essencial para configurações complexas ao vivo que requerem acesso a 40-80 configurações de botões em múltiplas músicas ou cenas.

### Visão Geral

**O que são Bancos?**
- Cada banco é um conjunto completo de configurações de botões (rótulos, cores, comandos MIDI)
- Seu dispositivo pode armazenar até 8 bancos
- Alterne entre bancos sem reconectar ao computador
- Cada banco mantém seus próprios estados de botão independentemente

**Casos de Uso Comuns:**
- **Seções de Música**: Banco 1 = Intro, Banco 2 = Verso, Banco 3 = Refrão, etc.
- **Múltiplas Músicas**: Cada banco representa uma música diferente
- **Camadas de Presets**: Banco 1 = Timbres de ritmo, Banco 2 = Timbres de solo, Banco 3 = Efeitos
- **Diferentes Dispositivos**: Banco 1 = Controle de amp, Banco 2 = Controle de efeitos, Banco 3 = Controle de DAW

### Gerenciando Bancos

O **Painel de Bancos** (na aba Botões) fornece acesso em abas para todos os seus bancos:

#### Adicionando um Banco
1. Clique no botão **+ Adicionar Banco**
2. Um novo banco aparece com configurações padrão de botões
3. O banco é automaticamente nomeado "Bank N" (personalizável)
4. Máximo de 8 bancos por dispositivo

#### Duplicando um Banco
1. Selecione o banco que deseja copiar
2. Clique no botão **Duplicar**
3. Uma cópia é criada com " (Cópia)" anexado ao nome
4. Útil para criar variações de configurações existentes

#### Renomeando um Banco
1. Clique no nome do banco para editar
2. Digite o novo nome (máximo 20 caracteres)
3. Pressione Enter ou clique fora para salvar
4. Os nomes aparecem no display do dispositivo durante a troca de banco

#### Deletando um Banco
1. Clique no botão **Deletar** na aba do banco
2. Confirme a exclusão
3. Não é possível deletar se restar apenas um banco
4. Configurações de bancos deletados não são recuperáveis

#### Editando Botões do Banco
1. Clique em uma aba de banco para torná-lo ativo
2. Toda edição de botão aplica-se ao banco ativo
3. O layout do dispositivo mostra a configuração de botões do banco ativo
4. Alterne entre bancos enquanto edita para configurar cada um

### Métodos de Troca de Banco

Escolha como alternar entre bancos no seu dispositivo:

#### Método 1: Troca por Botão

**Botão Único (Ciclando)**
- Pressione um botão para circular pelos bancos em ordem
- Retorna ao início: Banco 8 → Banco 1
- Simples e intuitivo para navegação sequencial

**Configuração:**
1. Selecione "Botão" como método de troca
2. Escolha o número do botão (1-10 para footswitches, 11 para encoder push no STD10)
3. Cada pressão avança para o próximo banco

**Botão Duplo (Acima/Abaixo)**
- Use dois botões: um para próximo banco, um para anterior
- Mais controle para navegação não-sequencial
- Recomendado para configurações com 4+ bancos

**Configuração:**
1. Selecione "Botão" como método de troca
2. Clique em "Alternar para Dois Botões (Acima/Abaixo)"
3. Defina o botão Banco Acima (ex: botão 10)
4. Defina o botão Banco Abaixo (ex: botão 9)

**Importante:** Botões atribuídos para troca de banco não podem ser usados para comandos MIDI regulares.

#### Método 2: Troca por MIDI CC

Troque bancos via mensagens MIDI Control Change recebidas:
- Controlador externo envia mensagem CC
- O valor CC mapeia diretamente para o índice do banco
- Valor 0 → Banco 1, Valor 1 → Banco 2, etc.

**Configuração:**
1. Selecione "CC" como método de troca
2. Defina o número CC (0-127)
3. Defina o canal MIDI (0-15 na config, exibido como 1-16)

**Exemplo:**  
Configure CC 80 no Canal 1. Quando sua DAW ou controlador envia `CC 80 = 2` no Canal 1, o dispositivo muda para o Banco 3.

#### Método 3: Troca por MIDI PC

Troque bancos via mensagens MIDI Program Change recebidas:
- Similar ao CC mas usa mensagens Program Change
- Configure o número PC base (ex: PC 0)
- Valores PC offset da base mapeiam para bancos

**Configuração:**
1. Selecione "PC" como método de troca
2. Defina o número PC base (0-127)
3. Defina o canal MIDI (0-15 na config, exibido como 1-16)

**Exemplo:**  
PC base = 10. Mensagens PC mapeiam da seguinte forma:
- PC 10 → Banco 1
- PC 11 → Banco 2
- PC 12 → Banco 3

### Comportamento da Troca de Banco

**Feedback Visual:**
- Todos os LEDs dos botões piscam brevemente em suas cores configuradas
- O nome do banco aparece no display central
- Status mostra "Bank N/Total" (ex: "Bank 2/4")

**Persistência de Estado:**
- Cada banco lembra seus estados de botão independentemente
- Trocar para outro banco e voltar preserva o estado
- Útil para manter cenas separadas

**Proteção de Cooldown:**
- Atraso mínimo de 200ms entre trocas de banco
- Previne trocas rápidas acidentais
- Garante transições de estado limpas

**Transição Instantânea:**
- Troca completa em menos de 100ms
- Sem interrupção da performance
- Botões do novo banco imediatamente responsivos

### Migração de Configurações de Banco Único

Configurações existentes migram automaticamente para o sistema de Bancos:
- Seus botões atuais se tornam "Banco 1"
- Nenhuma migração manual necessária
- Configuração original preservada e funcional
- Adicione mais bancos quando estiver pronto

### Exemplos de Configuração

**Setup de Banda ao Vivo (4 Bancos):**
- Banco 1: Música A (cenas de verso, refrão, ponte)
- Banco 2: Música B
- Banco 3: Música C
- Banco 4: Música D
- Use botões duplos (9 = anterior, 10 = próximo) para navegar

**Setup de Estúdio de Gravação (3 Bancos):**
- Banco 1: Armar trilhas e monitoração de entrada
- Banco 2: Controle de transporte e marcadores
- Banco 3: Automação de mix e efeitos
- Use MIDI CC da DAW para trocar bancos automaticamente

**Setup Multi-Dispositivo (2 Bancos):**
- Banco 1: Troca de canal de amp e reverb
- Banco 2: Pedais de stomp on/off e tempo de delay
- Use botão único ciclando para alternar entre dispositivos

---

## Configuração de Botões

### Identidade do Botão

**ID do Botão**  
Identificador único para referenciar este botão (ex: `btn1`, `cena_a`)

**Rótulo**  
Nome de exibição mostrado na tela do dispositivo (máximo 6 caracteres)

**Cor**  
Cor do LED da paleta predefinida:
- Vermelho, Verde, Azul
- Amarelo, Ciano, Magenta
- Laranja, Roxo, Branco

### Configurações de Comportamento

#### Modo

- **Toggle**: Botão alterna entre estados ON e OFF
  - Pressionar → liga, envia comandos Press
  - Pressionar novamente → desliga, envia comandos Release
  - LED permanece aceso quando ON

- **Momentary**: Botão fica ON apenas enquanto pressionado
  - Pressionar → liga, envia comandos Press
  - Soltar → desliga, envia comandos Release
  - Como um pedal de sustain

- **Select**: Botão liga quando pressionado, permanece ON
  - Usado com grupos de seleção para comportamento de botão de rádio
  - Pressionar → liga, envia comandos Press
  - Outros botões no mesmo grupo desligam automaticamente

- **Tap**: Modo avançado para tap tempo (recurso futuro)

#### Modo Off

Controla a aparência do LED quando o botão está OFF:
- **Dim**: LED visível com brilho reduzido (% configurável)
- **Off**: LED completamente apagado

#### Brilho Reduzido

Quando Modo Off é "Dim", defina a porcentagem de brilho (0-100%):
- **0%**: Completamente apagado
- **15%**: Brilho sutil padrão
- **50%**: Metade do brilho
- **100%**: Brilho total (aparece sempre ligado)

Pré-visualização em tempo real mostra a cor reduzida ao lado do controle deslizante.

#### Grupo de Seleção

Agrupe múltiplos botões para comportamento de botão de rádio:
- Atribua o mesmo nome de grupo a botões relacionados
- Quando um botão liga, outros no grupo desligam
- Botões desmarcados enviam seus comandos Release
- Útil para: seleção de cenas, troca de modos

**Exemplo**: Agrupe botões 1-4 como `"cenas"`. Pressionar botão 2 desliga botões 1, 3 e 4.

#### Selecionado por Padrão

Marque este botão para ativar na inicialização do dispositivo:
- Botão liga quando dispositivo inicia
- Envia comandos Press na inicialização
- Apenas um botão por grupo de seleção deve ser padrão

### Substituição de Canal

Substitua o canal MIDI global para este botão (1-16). Deixe em branco para usar canal global.

---

## Ações (Comandos MIDI)

Cada botão pode enviar diferentes comandos MIDI para quatro eventos:

### Tipos de Evento

1. **Press**: Enviado quando o botão é pressionado
2. **Release**: Enviado quando o botão é solto (ou alternado para OFF)
3. **Long Press**: Enviado quando o botão é mantido além do limite
4. **Long Release**: Enviado quando o botão é solto após long press

### Fontes de Ação

#### Ação de Perfil (Recomendado)

Use perfis integrados para dispositivos comuns:
- Selecione perfil de dispositivo (Quad Cortex, Helix, Kemper, etc.)
- Escolha ação no menu suspenso
- Comandos MIDI configurados automaticamente
- Pré-visualização mostra MIDI resolvido

Veja a seção [Perfis de Dispositivos](#perfis-de-dispositivos) para detalhes.

#### MIDI Personalizado

Configure comandos MIDI manualmente:

**Múltiplos Comandos Por Evento**  
Cada evento (Press, Release, etc.) pode enviar múltiplos comandos MIDI em sequência.

Clique em **+ Adicionar Comando** para adicionar mais comandos a um evento.

### Tipos de Comando

#### Control Change (CC)

Tipo de mensagem MIDI mais comum.

**Parâmetros:**
- **Tipo**: CC
- **Controller**: Número CC (0-127)
- **Valor**: Valor CC (0-127)
- **Canal**: Canal MIDI (1-16, opcional)

**Exemplo**: Enviar CC 20 com valor 127 no canal 1

**Usos Comuns:**
- Alternar efeitos (valor 127 = on, 0 = off)
- Controlar parâmetros (faixa 0-127)
- Trocar cenas/snapshots

#### Note On/Off (Note)

Enviar mensagens de nota MIDI.

**Parâmetros:**
- **Tipo**: Note
- **Nota**: Número da nota MIDI (0-127)
- **Velocity**: Velocidade da nota (0-127)
- **Canal**: Canal MIDI (1-16, opcional)

**Nota**: Velocity 0 = Note Off, Velocity > 0 = Note On

**Usos Comuns:**
- Acionar pads de bateria
- Alternar afinador (alguns dispositivos)
- Acionar samples

#### Program Change (PC)

Mudar presets/patches.

**Parâmetros:**
- **Tipo**: PC
- **Programa**: Número do programa (0-127)
- **Canal**: Canal MIDI (1-16, opcional)

**Usos Comuns:**
- Trocar presets
- Mudar patches
- Selecionar bancos

#### Program Change Inc (PC+)

Incrementar número do programa por valor de passo.

**Parâmetros:**
- **Tipo**: PC Inc
- **Passo**: Quantidade de incremento (padrão 1)
- **Canal**: Canal MIDI (1-16, opcional)

**Uso Comum**: Botão de próximo preset/patch

#### Program Change Dec (PC-)

Decrementar número do programa por valor de passo.

**Parâmetros:**
- **Tipo**: PC Dec
- **Passo**: Quantidade de decremento (padrão 1)
- **Canal**: Canal MIDI (1-16, opcional)

**Uso Comum**: Botão de preset/patch anterior

### Limite de Long Press

Para comandos Long Press, defina a duração de manutenção em milissegundos:
- Padrão: **500ms** (meio segundo)
- Faixa: 100-5000ms
- Aplica-se apenas ao primeiro comando Long Press

**Exemplo**: Defina 1000ms para exigir 1 segundo de manutenção antes de acionar

### Duração do Flash (Comandos PC)

Para botões Program Change sem estado persistente:
- Defina duração do flash do LED em milissegundos
- Padrão: **200ms**
- Fornece feedback visual para pressionamento momentâneo

---

## Perfis de Dispositivos

Perfis de dispositivos simplificam a configuração convertendo ações de alto nível em comandos MIDI.

### Perfis Disponíveis

#### Neural DSP Quad Cortex
- Seleção de cenas A/B/C/D
- Bypass de Stomp e Row
- Controle de afinador
- Navegação de presets

#### Line 6 Helix
- Seleção de snapshot (1-8)
- Atribuições de footswitch
- Controles de looper
- Alternância de afinador

#### Line 6 HX Stomp
- Seleção de snapshot (1-3)
- Emulação de footswitch
- Controle de pedal de expressão

#### Kemper Profiler
- Seleção de rig
- Bypass de efeito
- Controle de afinador
- Funções de looper

#### Ableton Live (Template)
- Lançamento de cena
- Mute/solo de faixa
- Controle de transporte
- Controle de dispositivo

#### Apple MainStage (Template)
- Mudanças de patch
- Controles de bypass
- Mapeamento de expressão

### Usando Perfis

1. **Selecione Evento**: Escolha Press, Release, Long Press ou Long Release
2. **Altere Fonte**: Selecione "Ação de Perfil"
3. **Escolha Dispositivo**: Selecione perfil de dispositivo alvo
4. **Selecione Ação**: Escolha ação no menu suspenso
5. **Pré-visualize MIDI**: Visualize comandos resolvidos
6. **Substituição de Canal**: Opcionalmente substitua canal MIDI

### Substituições de Canal

Cada ação de perfil pode substituir seu canal MIDI padrão:
- Deixe em branco para usar padrão do perfil
- Defina canal específico (1-16) para roteamento personalizado

### Combinando Comandos de Perfil e Personalizados

Você pode misturar ações de perfil e comandos personalizados no mesmo evento:
- Adicione ação de perfil
- Clique em **+ Adicionar Comando**
- Adicione comandos CC, Note ou PC personalizados
- Comandos executam em sequência

### Auto-Detecção

Quando você seleciona um botão, o editor mostra se os comandos MIDI existentes correspondem a um perfil conhecido:
- **Indicador de badge**: Mostra perfil correspondente
- **Tooltip**: Exibe nome do perfil detectado
- Facilita identificar botões pré-configurados

---

## Ações Condicionais

Ações Condicionais permitem que botões executem diferentes comandos MIDI baseados em condições em tempo real. Isso cria um comportamento inteligente e sensível ao contexto que se adapta à sua performance.

### O Que São Ações Condicionais?

Uma ação condicional usa lógica **SE/ENTÃO/SENÃO**:
- **SE** uma condição é verdadeira (ex: "Botão 2 está ON")
- **ENTÃO** execute estes comandos
- **SENÃO** execute estes outros comandos

Isso permite que um único botão se comporte diferentemente dependendo do estado de outros botões, mensagens MIDI recebidas, posição do pedal de expressão ou valor do encoder.

### Quando Usar Condicionais

**Casos de Uso Comuns:**
- Enviar diferentes valores CC baseados em qual cena está ativa
- Alternar entre duas configurações de efeito dependendo da seleção de canal
- Responder diferentemente quando o host envia mensagens MIDI específicas
- Ajustar comportamento baseado na posição do pedal de expressão
- Criar botões "inteligentes" que se adaptam ao contexto da performance

### Os 5 Tipos de Condição

#### 1. Estado do Botão

Verifica se outro botão está atualmente ON ou OFF.

**Campos:**
- **Botão**: Qual botão verificar (por índice)
- **Estado**: "on" ou "off"

**Exemplo:**  
*"Se botão Drive (botão 1) está ON, envie CC50=127, senão envie CC50=0"*

**Caso de Uso:** Efeito de delay que se comporta diferentemente baseado em se a distorção está ativa

#### 2. Keytime do Botão

Verifica em qual estado de keytime um botão multi-estado está atualmente.

**Campos:**
- **Botão**: Qual botão verificar
- **Keytime**: Índice do estado (0 = primeiro estado, 1 = segundo estado, etc.)

**Exemplo:**  
*"Se botão Scene (botão 0) está no keytime 2, envie PC5, senão envie PC1"*

**Caso de Uso:** Diferentes configurações de boost para cada cena

#### 3. MIDI Recebido

Verifica o valor de uma mensagem MIDI CC recebida do host.

**Campos:**
- **Canal**: Canal MIDI (0-15)
- **Número CC**: Número do controlador a verificar
- **Operador**: Tipo de comparação (==, !=, >, <, >=, <=)
- **Valor**: Valor para comparar (0-127)

**Exemplo:**  
*"Se CC100 recebido no canal 0 >= 64, envie CC25=127, senão envie CC25=0"*

**Caso de Uso:** Comportamento do botão muda baseado no que a DAW envia (sincronização bidirecional)

#### 4. Pedal de Expressão

Verifica a posição atual de um pedal de expressão.

**Campos:**
- **Pedal**: "exp1" ou "exp2"
- **Operador**: Tipo de comparação (==, !=, >, <, >=, <=)
- **Valor**: Valor para comparar (0-127)

**Exemplo:**  
*"Se exp1 < 30, envie PC0, senão envie PC1"*

**Caso de Uso:** Trocar cenas automaticamente baseado na posição do pedal (ponta vs calcanhar)

#### 5. Posição do Encoder

Verifica o valor atual do encoder rotativo.

**Campos:**
- **Operador**: Tipo de comparação (==, !=, >, <, >=, <=)
- **Valor**: Valor para comparar (0-127)

**Exemplo:**  
*"Se encoder >= 64, envie CC30=127, senão envie CC30=64"*

**Caso de Uso:** Diferente intensidade de efeito baseada na posição do encoder

### Criando Comandos Condicionais

#### Passo 1: Adicionar um Comando Condicional

1. Selecione um botão
2. Vá para a seção **Ações**
3. Escolha um evento (Press, Release, Long Press, Long Release)
4. Clique em **+ Adicionar Comando**
5. Selecione **"Conditional"** no menu suspenso Tipo

#### Passo 2: Construir a Condição

O Construtor de Condição aparece com:
- Menu suspenso **Tipo de Condição** (Estado do Botão, Keytime do Botão, etc.)
- **Campos específicos do tipo** (índice do botão, número CC, operador, valor)

1. Selecione tipo de condição
2. Preencha os campos requeridos
3. A condição é avaliada quando o botão é pressionado

#### Passo 3: Definir Comandos ENTÃO

1. Na seção **"ENTÃO"**, clique em **+ Adicionar Comando**
2. Adicione comandos MIDI que executam se a condição for VERDADEIRA
3. Pode adicionar múltiplos comandos (eles executam em sequência)
4. Suporta CC, Note, PC, PC Inc/Dec, e até condicionais aninhadas

#### Passo 4: Definir Comandos SENÃO (Opcional)

1. Na seção **"SENÃO"**, clique em **+ Adicionar Comando**
2. Adicione comandos MIDI que executam se a condição for FALSA
3. Seção SENÃO é opcional (nada acontece se condição for falsa)

#### Passo 5: Adicionar Rótulos de Display (Opcional)

**Rótulo ENTÃO:**  
Texto para mostrar no display quando o ramo ENTÃO executa (máx 6 caracteres)

**Rótulo SENÃO:**  
Texto para mostrar no display quando o ramo SENÃO executa (máx 6 caracteres)

**Persistir Rótulo:**  
Caixa de seleção - se habilitado, rótulos condicionais permanecem visíveis; se desabilitado, expiram após 3 segundos

### Exemplos do Mundo Real

#### Exemplo 1: Delay Sensível à Cena

**Objetivo:** Botão de delay envia diferentes valores CC baseado na cena ativa

**Configuração:**
- Botão 0 = cena "CLEAN" (toggle)
- Botão 3 = "DELAY" com condicional

**Configuração do Botão 3:**
```
Press:
  - Tipo: Conditional
    SE: Estado do Botão
      Botão: 0
      Estado: on
    ENTÃO:
      - CC 22, Valor 64  (delay baixo para clean)
    SENÃO:
      - CC 22, Valor 127 (delay máximo para drive)
    Rótulo ENTÃO: "DLY LO"
    Rótulo SENÃO: "DLY HI"
```

**Resultado:** Quando CLEAN está ativo, delay é sutil; quando drive está ativo, delay é máximo

#### Exemplo 2: Troca Automática Baseada em Expressão

**Objetivo:** Botão troca cenas automaticamente baseado na posição do pedal de expressão

**Configuração:**
- Botão 5 = "CENA AUTO"

**Configuração do Botão 5:**
```
Press:
  - Tipo: Conditional
    SE: Expressão
      Pedal: exp1
      Operador: <
      Valor: 40
    ENTÃO:
      - PC 0  (cena 1 quando calcanhar abaixado)
    SENÃO:
      - PC 1  (cena 2 quando ponta levantada)
```

**Resultado:** Pressione botão uma vez, cena muda automaticamente baseado na posição do pedal

#### Exemplo 3: Botão Responsivo ao Host

**Objetivo:** Comportamento do botão muda baseado no estado da DAW

**Configuração:**
- DAW envia CC100=127 quando gravando, CC100=0 quando parado
- Botão 8 = "REC SMART"

**Configuração do Botão 8:**
```
Press:
  - Tipo: Conditional
    SE: MIDI Recebido
      Canal: 0
      CC: 100
      Operador: ==
      Valor: 127
    ENTÃO:
      - CC 50, Valor 0    (parar gravação)
    SENÃO:
      - CC 50, Valor 127  (iniciar gravação)
```

**Resultado:** Botão alterna gravação, adaptando-se ao estado atual da DAW

#### Exemplo 4: Boost Multi-Cena

**Objetivo:** Botão boost envia CC diferente baseado em qual botão de cena está ativo

**Configuração:**
- Botão 0 = Cena 1 (keytime 0)
- Botão 0 = Cena 2 (keytime 1)
- Botão 0 = Cena 3 (keytime 2)
- Botão 6 = "BOOST" com condicionais

**Configuração do Botão 6:**
```
Press:
  - Tipo: Conditional
    SE: Keytime do Botão
      Botão: 0
      Keytime: 0
    ENTÃO:
      - CC 70, Valor 127  (boost clean)
    SENÃO:
      - Tipo: Conditional
        SE: Keytime do Botão
          Botão: 0
          Keytime: 1
        ENTÃO:
          - CC 71, Valor 127  (boost crunch)
        SENÃO:
          - CC 72, Valor 127  (boost lead)
```

**Resultado:** Botão boost ativa diferentes CCs de boost para cada cena (condicionais aninhadas)

### Recursos Avançados

#### Condicionais Aninhadas

Condicionais podem ser aninhadas dentro dos ramos ENTÃO/SENÃO para árvores de lógica complexas:
- SE botão 1 está ON
  - ENTÃO SE botão 2 está ON
    - ENTÃO envie CC30=127
    - SENÃO envie CC30=64
  - SENÃO envie CC30=0

**Limite de profundidade:** Sem limite rígido, mas 2-3 níveis é tipicamente suficiente

#### Misturando Condicionais com Comandos Regulares

Você pode misturar comandos MIDI condicionais e regulares no mesmo evento:
```
Press:
  - CC 10, Valor 127        (sempre envia isso)
  - Tipo: Conditional       (comando condicional)
    SE: ...
    ENTÃO: ...
  - PC 5                    (sempre envia isso após condicional)
```

Comandos executam na ordem em que aparecem.

#### Avaliação de Snapshot de Estado

Ao usar condições de Estado do Botão ou Keytime do Botão:
- Condição é avaliada usando o estado do botão **no momento do pressionamento**
- Isso garante comportamento consistente mesmo se outros botões mudarem durante a execução
- Previne condições de corrida em configurações complexas

### Elementos da Interface

**Construtor de Condição:**
- Menu suspenso para seleção de tipo de condição
- Campos dinâmicos baseados no tipo selecionado
- Filtragem de rótulo de botão (não pode referenciar o botão que está editando)

**Bloco de Comando Condicional:**
- Estrutura SE/ENTÃO/SENÃO recolhível
- Aninhamento visual para clareza
- Ramos codificados por cor (verde para ENTÃO, vermelho para SENÃO)
- Alças de arrasto para reordenação (se aplicável)

**Campos de Rótulo:**
- Entradas de texto de Rótulo Então e Rótulo Senão
- Limite de 6 caracteres
- Caixa de seleção de persistência opcional

### Dicas e Melhores Práticas

**Comece Simples:**
- Comece com lógica SE/ENTÃO básica antes de aninhar
- Teste cada condição individualmente
- Use rótulos de display para verificar qual ramo executou

**Evite Auto-Referência:**
- Não verifique o estado do botão que está editando
- A interface previne isso, mas é conceitualmente importante

**Use Rótulos para Depuração:**
- Defina rótulos ENTÃO/SENÃO para ver qual ramo executou
- Útil durante configuração e solução de problemas

**Valores de Limiar de Expressão:**
- Pedais de expressão leem 0-127
- Use < 30 para "calcanhar abaixado", > 100 para "ponta levantada"
- Evite igualdade exata (==) devido a jitter

**Sincronização MIDI Recebido:**
- Certifique-se de que seu host/DAW está enviando os valores CC esperados
- Use Monitor MIDI para verificar mensagens recebidas
- Números de canal são indexados em 0 nas condições (0 = canal MIDI 1)

**Considerações de Performance:**
- Condicionais são avaliadas rapidamente (< 1ms)
- Sem latência perceptível mesmo com condicionais aninhadas
- Seguro para usar em performance ao vivo

### Solução de Problemas

**Condicional Não Disparando:**
- Verifique se os campos de condição estão corretos (índice do botão, número CC, canal)
- Verifique se a condição é realmente verdadeira (use Monitor MIDI)
- Certifique-se de que os ramos ENTÃO/SENÃO têm comandos adicionados

**Ramo Errado Executando:**
- Verifique novamente o operador (>, <, ==, etc.)
- Verifique se o valor de limiar está correto
- Use rótulos de display para confirmar qual ramo executou

**Confusão de Índice de Botão:**
- Índices de botão são baseados em 0: Botão 1 = índice 0, Botão 2 = índice 1
- A interface mostra rótulos de botão para clareza
- Confira Layout do Dispositivo para confirmar números de botão

**Rótulo de Display Não Aparecendo:**
- Rótulo deve ter 6 caracteres ou menos
- Verifique se conditional_label_persist está habilitado na configuração do botão
- Botões não-select expiram após 3 segundos a menos que persistir esteja habilitado

---

## Botões Multi-Estado (Keytimes)

Keytimes permitem que botões ciclem por múltiplos estados, enviando diferentes comandos MIDI a cada pressão.

### Habilitando Keytimes

1. Selecione um botão
2. Encontre o campo **Keytimes** em Comportamento
3. Defina número de estados (2-8)
4. Abas de estado aparecem abaixo de Ações

### Configuração de Estado

Cada estado pode substituir:
- **Número CC**: Controlador diferente por estado
- **Valor CC On**: Valor diferente quando ativo
- **Cor**: Cor de LED diferente por estado
- **Rótulo**: Nome de exibição diferente por estado

### Ciclo de Estados

**Modo Toggle/Select:**
- Primeiro pressionar → Estado 1 (envia comandos Press)
- Segundo pressionar → desliga (envia comandos Release)
- Terceiro pressionar → Estado 2 (envia comandos Press)
- Quarto pressionar → desliga (envia comandos Release)
- E assim por diante...

**Exemplo - Ciclo de Cenas:**

Botão rotulado "CENAS" com 3 keytimes:
- **Estado 1**: CC 20, LED Vermelho, "LIMPO"
- **Estado 2**: CC 21, LED Verde, "CRUNCH"
- **Estado 3**: CC 22, LED Azul, "LEAD"

Cada pressão cicla através de limpo → crunch → lead → off → limpo...

### Abas de Estado

Quando keytimes > 1, abas aparecem para cada estado:
- Clique na aba para editar substituições daquele estado
- Estado ativo destacado em cor
- Deixe campos vazios para usar configurações base do botão

---

## Configuração do Encoder

*Disponível apenas no modelo STD10*

O encoder rotativo fornece controle contínuo e funcionalidade de botão de pressão.

### Rotação do Encoder

**Habilitar/Desabilitar**  
Alterne funcionalidade do encoder on/off

**Número CC**  
Controlador MIDI a enviar (0-127)

**Rótulo**  
Nome de exibição (máximo 8 caracteres)

**Faixa (Min/Max)**  
- Min: Valor inicial (0-127)
- Max: Valor final (0-127)
- Initial: Posição inicial no boot

**Passos**  
Número de passos discretos (deixe em branco para contínuo)

**Canal**  
Canal MIDI (1-16), usa canal global se em branco

### Botão de Pressão do Encoder

O encoder tem um botão de pressão integrado com capacidades completas de botão:

**Habilitar/Desabilitar**  
Alterne funcionalidade do botão de pressão

**Modo**  
- Toggle
- Momentary

**Números CC**  
- CC On: Valor enviado quando ligado (0-127)
- CC Off: Valor enviado quando desligado (0-127)

**Configurações de Display**
- Rótulo: Nome do botão (máximo 8 caracteres)
- Canal: Substituição de canal MIDI (1-16)

---

## Pedais de Expressão

*Disponível apenas no modelo STD10*

Configure até duas entradas de pedal de expressão (EXP1 e EXP2).

### Configurações de Expressão

**Habilitar/Desabilitar**  
Alterne entrada de pedal de expressão

**Número CC**  
Controlador MIDI a enviar (0-127)

**Rótulo**  
Nome de exibição (máximo 8 caracteres)

**Faixa (Min/Max)**  
- Min: Valor na posição de calcanhar (0-127)
- Max: Valor na posição de ponta (0-127)

**Polaridade**  
- Normal: Min no calcanhar, Max na ponta
- Invertido: Max no calcanhar, Min na ponta

**Limite (Threshold)**  
Movimento mínimo para registrar mudança (reduz instabilidade)

**Canal**  
Canal MIDI (1-16), usa canal global se em branco

---

## Configurações de Display

Personalize tamanhos de texto na tela do dispositivo.

### Opções de Tamanho de Texto

**Texto de Botão**  
Rótulos exibidos para cada slot de botão
- Pequeno: Compacto (~8px)
- Médio: Padrão (20px)
- Grande: Negrito (60px)

**Texto de Status**  
Linha de status central (mensagens MIDI, info do sistema)
- Pequeno: Compacto (~8px)
- Médio: Padrão (20px)
- Grande: Negrito (60px)

**Texto de Expressão**  
Exibição de valor do pedal de expressão
- Pequeno: Compacto (~8px)
- Médio: Padrão (20px)
- Grande: Negrito (60px)

**Nota**: Texto muito grande pode transbordar o display para rótulos longos. Use Médio para aparência balanceada.

---

## Monitor MIDI

O **Monitor MIDI** é uma ferramenta profissional de depuração integrada no editor de configuração que exibe tráfego MIDI em tempo real entre seu dispositivo e outros equipamentos MIDI.

### Abrindo o Monitor

1. Clique no botão **Monitor MIDI** na barra de ferramentas (barra inferior)
2. O painel do monitor abre na parte inferior do editor
3. Clique novamente para fechar o painel

### Visão Geral da Interface

**Controles do Cabeçalho**
- **Seletor de Porta**: Escolha qual porta MIDI monitorar
- **Pausar/Retomar**: Pausa a captura de mensagens mantendo o monitor aberto
- **Limpar**: Deleta todas as mensagens capturadas
- **Exportar**: Salva o log de mensagens em um arquivo .txt com timestamp
- **Auto-rolagem**: Alterna rolagem automática para mensagens mais recentes (habilitado por padrão)

**Barra de Filtros**
- **Tipo**: Filtrar por tipo de mensagem (CC, Note On, Note Off, PC, SysEx, ou Todos)
- **Canal**: Filtrar por canal MIDI 1-16 (ou Todos os canais)
- **Direção**: Filtrar por IN (entrada), OUT (saída), ou Todos

**Exibição de Mensagens**
- Cada mensagem mostra: timestamp, direção, canal, tipo de mensagem e dados
- **Badges de tipo com código de cores**: 
  - ● CC (Control Change)
  - ▲ Note On
  - ▼ Note Off
  - ■ PC (Program Change)
  - ◆ SysEx (System Exclusive)
  - ○ Outro
- Mensagens são exibidas mais recente primeiro (mais nova no topo)
- Badge mostra contagem filtrada / total (ex: "24 / 150")

### Casos de Uso Comuns

**1. Depuração de Configuração de Botão**

Ao configurar um botão, use o monitor para verificar:
- **Números CC corretos** são enviados
- **Canal** corresponde ao seu dispositivo alvo
- **Valores** (0-127) estão conforme esperado
- **Sequências multi-comando** executam em ordem

**Exemplo de fluxo de trabalho:**
1. Abra o Monitor MIDI
2. Pressione o botão no dispositivo
3. Verifique se a mensagem aparece com parâmetros corretos
4. Se estiver errado, ajuste a config do botão e teste novamente

**2. Aprendendo MIDI de Dispositivos Externos**

Para mapear botões para corresponder à saída MIDI de um dispositivo externo:
1. Selecione a **saída MIDI do dispositivo externo** no seletor de porta
2. Configure o filtro para direção **IN** (entrada)
3. Acione a ação no dispositivo externo (mudar preset, habilitar efeito, etc.)
4. **Anote o CC#, canal e valores** no monitor
5. Configure seu botão MIDI Captain para enviar a mesma mensagem

**Exemplo:** Para aprender qual MIDI seu Helix envia para "Snapshot 3":
- Monitor: `12:34:56.789 IN Ch1 CC 69 = 2`
- Configure botão: CC 69, Valor 2, Canal 1

**3. Verificando Sincronização Bidirecional**

Teste se seu software host está enviando MIDI de volta para o controlador:
1. Configure filtro para direção **IN**
2. Mude um parâmetro no seu DAW/host de plugin
3. Se MIDI bidirecional está funcionando, você verá mensagens CC/PC de entrada
4. Verifique se o CC# e canal correspondem à configuração do seu botão

**4. Testando Ações Multi-Comando**

Quando um botão envia múltiplos comandos MIDI:
1. Limpe o log antes de testar
2. Pressione o botão uma vez
3. Conte o número de mensagens (deve corresponder aos comandos configurados)
4. Verifique a ordem de execução

**5. Calibração de Pedal de Expressão**

Verifique saída MIDI do pedal de expressão:
1. Filtre por tipo **CC** e o número CC atribuído ao pedal
2. Mova o pedal através de toda a faixa
3. Verifique valor Min na posição de calcanhar
4. Verifique valor Max na posição de ponta
5. Observe por ruído ou saltos inesperados (aumente threshold se necessário)

### Exemplos de Formato de Mensagem

**Control Change:**
```
12:34:56.123 OUT Ch1 CC20 = 127
```
- Timestamp: 12:34:56 com precisão de 123ms
- Direção: OUT (enviado pelo MIDI Captain)
- Canal: 1
- Tipo: Control Change #20
- Valor: 127

**Note On:**
```
12:34:57.456 IN Ch10 Note 60 ON (vel 100)
```
- Direção: IN (recebido pelo MIDI Captain)
- Canal: 10 (canal de bateria)
- Nota: 60 (Dó Central)
- Velocidade: 100

**Program Change:**
```
12:34:58.789 OUT Ch1 PC 5
```
- Program Change para programa #5

**SysEx:**
```
12:34:59.012 IN SysEx [24 bytes]
```
- Mensagem System Exclusive (específica do fabricante)
- Contagem de bytes mostrada entre colchetes

### Estratégias de Filtragem

**Focar em Botão Específico:**
1. Configure filtro de **Tipo** para o tipo de mensagem usado pelo botão (ex: CC)
2. Filtre pelo **Canal** do botão
3. Anote o CC# específico na mensagem
4. Apenas mensagens correspondendo tanto tipo quanto canal aparecerão

**Monitorar MIDI Clock:**
- MIDI Clock é um tipo específico de mensagem (não CC/Note/PC)
- Desabilite todos os filtros para ver mensagens de clock
- Ou filtre **Tipo: Outro** para excluir mensagens padrão

**Capturar Apenas Saída:**
- Configure **Direção: OUT**
- Mostra apenas mensagens enviadas pelo MIDI Captain
- Útil para verificar que pressionar botões funciona

**Observar Feedback do Host:**
- Configure **Direção: IN**
- Mostra apenas mensagens recebidas do host/DAW
- Útil para depurar sincronização bidirecional

### Exportação e Análise

**Formato de Exportação:**

Clicar em **Exportar** salva mensagens em um arquivo de texto:
```
Nome do arquivo: midi-log-1711238794123.txt

12:34:56.123 OUT Ch1 CC20 = 127
12:34:56.456 OUT Ch1 CC21 = 64
12:34:57.789 IN Ch1 CC20 = 127
```

**Casos de Uso:**
- Compartilhar logs ao reportar problemas
- Comparar saída MIDI esperada vs real
- Documentar implementação MIDI para configurações complexas
- Arquivar configurações funcionais

### Notas de Performance

**Tamanho do Buffer:**
- O monitor armazena até **1000 mensagens**
- Mensagens mais antigas são removidas automaticamente quando o buffer está cheio
- Para streams de altíssimo throughput (MIDI clock), considere pausar periodicamente

**MIDI de Alto Throughput:**

O monitor usa um ring buffer otimizado que pode lidar com:
- MIDI Clock (24 mensagens por semínima)
- Streams de CC densos (movimentos rápidos de knob)
- Múltiplos dispositivos simultâneos

**Se experimentar lag:**
1. Use filtros para reduzir contagem de mensagens
2. Feche outras aplicações usando MIDI
3. Pause monitoramento quando não estiver depurando ativamente

### Dicas

- **Deixe o monitor aberto durante configuração** para ver feedback imediato
- **Use Limpar frequentemente** para focar nas mensagens mais recentes
- **Pause antes de inspecionar** uma mensagem específica em detalhe
- **Exporte antes de fechar** se precisar referenciar mensagens depois
- **Filtre agressivamente** para configurações MIDI complexas com muitos dispositivos
- **Verifique direção** — IN vs OUT ajuda a isolar fonte de comportamento inesperado

### Solução de Problemas

**Nenhuma Mensagem Aparecendo:**
1. Verifique se **porta está selecionada** no dropdown
2. Confira se **dispositivo está conectado** e ligado
3. Garanta que **cabo MIDI** está conectado (se usando DIN de 5 pinos)
4. Tente **pressionar um botão configurado** para testar mensagens OUT
5. Verifique se **USB MIDI** está funcionando (confira configurações MIDI do sistema)

**Mensagens do Dispositivo Errado:**
1. Confira dropdown do **seletor de porta**
2. Algumas interfaces MIDI criam múltiplas portas virtuais
3. Selecione a porta específica para seu dispositivo

**Filtro Não Funcionando:**
1. Mensagens são filtradas no cliente (todas as mensagens ainda são capturadas)
2. Confira se **badge de filtro** mostra contagem filtrada/total
3. Tente **Limpar** e teste novamente
4. Canal deve ser **correspondência exata** (ex: "1" ≠ "Todos")

**Arquivo de Exportação Vazio:**
1. Garanta que **mensagens foram capturadas** antes de exportar
2. Confira **pasta Downloads** por arquivo .txt
3. Tente **Limpar, capturar mensagens, depois Exportar**

---

## Atalhos de Teclado

### Global

- **⌘S** / **Ctrl+S**: Salvar configuração no dispositivo
- **⌘Z** / **Ctrl+Z**: Desfazer última alteração
- **⌘⇧Z** / **Ctrl+Shift+Z**: Refazer alteração
- **⌘R** / **Ctrl+R**: Recarregar configuração do dispositivo
- **Esc**: Fechar diálogos modais

### Seleção de Botão

- **↑** / **↓**: Selecionar botão anterior/próximo
- **1-9, 0**: Seleção rápida de botão por número

### Copiar/Colar

- **⌘C** / **Ctrl+C**: Copiar botão selecionado (quando focado)
- **⌘V** / **Ctrl+V**: Colar configuração de botão

---

## Dicas e Melhores Práticas

### Fluxo de Trabalho de Configuração

1. **Comece com perfis** quando possível - eles lidam com MIDI complexo corretamente
2. **Use grupos de seleção** para botões mutuamente exclusivos (cenas, modos)
3. **Teste um botão de cada vez** antes de configurar o controlador inteiro
4. **Salve frequentemente** (⌘S) - alterações são escritas apenas ao salvar
5. **Use rótulos descritivos** - 6 caracteres são suficientes para identificar função

### Modos de Botão

- **Toggle**: Melhor para efeitos on/off (delay, reverb, looper)
- **Momentary**: Melhor para manter-enquanto-ativo (sustain, freeze, tap tempo)
- **Select**: Melhor para cenas, presets ou seleção de modo

#### Modo One-Shot / Trigger (Perfeito para Pads de Bateria!)

Para enviar MIDI **apenas ao pressionar** sem nenhuma mensagem de liberação (como um pad de bateria ou trigger de sample), deixe o evento **Release** vazio:

1. Defina o **Modo** do botão como **Momentary**
2. Adicione comandos ao evento **Press** (ex: Nota 36, velocity 127)
3. Deixe o evento **Release** completamente vazio
4. Pronto!

**O que acontece:**
- **Pressionar botão** → LED acende, envia mensagem MIDI
- **Segurar botão** → LED fica aceso, **sem mensagens repetidas** (enviado apenas uma vez ao pressionar)
- **Soltar botão** → LED apaga, **nada é enviado** (silencioso)
- **Pressionar novamente** → LED acende, envia mensagem MIDI novamente

**Perfeito para kits de bateria!** Cada pressão aciona o som, o LED fornece feedback visual, e você obtém o mesmo comportamento toda vez que pressiona - sem mensagens indesejadas de "note off".

**Importante:** O modo Momentary **NÃO envia continuamente** enquanto pressionado - ele envia **uma vez** ao pressionar e **uma vez** ao soltar. Ao deixar Release vazio, você obtém triggers one-shot limpos, ideais para bateria e samples.

Isso também funciona com o modo Toggle:
- **Toggle**: Envia MIDI apenas ao ligar, nada ao desligar

**Casos de uso:**
- Drum machines ou samplers (acionar sons)
- Efeitos one-shot (reverb/delay "dispara e esquece")
- Cues de iluminação ou triggers de cena
- Qualquer dispositivo que espera apenas mensagens de trigger (sem estado "off")

#### Modo Repetição (Mesma Mensagem a Cada Pressão)

Para enviar a **mesma mensagem MIDI toda vez** que você pressiona o botão (em vez de alternar ON/OFF), use o modo **Toggle** com **comandos idênticos** nos eventos Press e Release:

**Configuração:**
1. Defina o **Modo** do botão como **Toggle**
2. Adicione comandos ao evento **Press** (ex: CC64=127)
3. Adicione **os mesmos comandos** ao evento **Release** (CC64=127)

**Resultado:**
- Primeira pressão → botão liga, envia comandos Press
- Segunda pressão → botão desliga, envia comandos Release (idênticos aos Press)
- Terceira pressão → botão liga, envia comandos Press novamente
- Etc.

O botão alterna o estado visual (LED on/off) mas envia a mesma mensagem MIDI toda vez!

**Casos de uso:**
- **Tap tempo**: Enviar mesmo CC repetidamente para detecção de BPM
- **Avançar cena**: Incrementar número da cena a cada pressão
- **MIDI sync/nudge**: Mensagens de sincronização repetidas
- **Cues de iluminação**: Avançar para próxima cue a cada pressão
- Qualquer dispositivo que espera o mesmo valor de trigger repetidamente

**Feedback visual:** O LED ainda alternará entre estados ON e OFF a cada pressão, dando confirmação visual de que o botão registrou sua pressão.

### Canais MIDI

- Use **canal global** a menos que precise de múltiplos dispositivos
- **Substitua canal** por botão para configurações multi-dispositivo
- Lembre-se: Canal exibido como 1-16, armazenado como 0-15 internamente

### Ações Multi-Comando

- Ordem importa - comandos executam em sequência
- Mantenha comandos Press simples para resposta instantânea
- Use comandos Release para desabilitar efeitos de forma limpa
- Long Press para "função alternativa" no mesmo botão

### Dicas de Performance

- **Desabilite modo dev** para uso ao vivo (boot mais rápido, sem atraso USB)
- **Use Modo Off: Dim** para ver layout de botões no escuro
- **Defina default_selected** para cena/modo de inicialização
- **Teste grupos de seleção** minuciosamente - configuração errada pode causar conflitos

### Pedais de Expressão

- **Calibre a faixa** usando Min/Max para corresponder ao curso do seu pedal
- **Aumente o limite** se valores pularem erraticamente
- **Inverta polaridade** se pedal responder ao contrário

---

## Solução de Problemas

### Dispositivo Não Detectado

**Problema**: Dispositivo não aparece no menu suspenso

**Soluções**:
1. **Habilite modo USB drive**:
   - Desligue o dispositivo
   - Segure Switch 1 (superior esquerdo)
   - Ligue mantendo pressionado
   - Solte após 2 segundos
2. **Habilite modo dev** no config.json existente:
   - Adicione `"dev_mode": true` ao arquivo de configuração
   - Dispositivo sempre montará USB
3. **Verifique cabo USB** - deve ser cabo de dados, não apenas de carga
4. **Tente porta USB diferente** - algumas portas podem ter problemas
5. **Reinicie o editor** após conectar dispositivo

### Configuração Não Salvando

**Problema**: Alterações não persistem após salvar

**Soluções**:
1. Verifique **erros de validação** na barra de status
2. Certifique-se que dispositivo **não está protegido contra gravação**
3. Verifique se **USB drive tem espaço** (improvável mas possível)
4. Tente **Recarregar** e então salvar novamente
5. Verifique console para mensagens de erro

### Botão Não Respondendo

**Problema**: Pressionamentos de botão não enviam MIDI

**Soluções**:
1. Verifique **comandos MIDI** estão configurados para evento Press
2. Verifique **canal MIDI** corresponde ao dispositivo receptor
3. Certifique-se **números CC/Note** estão corretos para dispositivo alvo
4. Teste com **monitor MIDI** para verificar mensagens sendo enviadas
5. Tente **comando CC simples** primeiro para isolar problema

### Cor ou Comportamento Errado do LED

**Problema**: LED não corresponde à configuração

**Soluções**:
1. **Salve configuração** primeiro (alterações não aplicam até salvar)
2. **Reinicie dispositivo** após salvar
3. Verifique **Modo Off** - Dim vs Off afeta aparência
4. Verifique **nome da cor** está na paleta predefinida
5. Verifique **substituições de estado** se usar keytimes

### Encoder Não Funcionando

**Problema**: Encoder não envia MIDI

**Soluções**:
1. Verifique **encoder está habilitado** na configuração
2. Verifique **número CC** não conflita com botões
3. Certifique-se **faixa Min/Max** está correta (Min < Max)
4. Teste com software **monitor MIDI**
5. **Apenas STD10** - Mini6 não tem encoder

### Problemas com Pedal de Expressão

**Problema**: Pedal envia valores errados ou pula

**Soluções**:
1. **Calibre Min/Max** para corresponder à faixa real do pedal
2. **Aumente limite** para reduzir ruído/instabilidade
3. Tente **Polaridade Invertida** se faixa estiver ao contrário
4. Verifique **pedal é TRS** pedal de expressão (não TS)
5. Teste **pedal com multímetro** para verificar curso de resistência

### Display Mostra Texto Errado

**Problema**: Tela do dispositivo não corresponde à configuração

**Soluções**:
1. **Salve e reinicie** dispositivo
2. Verifique **comprimento máximo do rótulo** (6 caracteres para botões, 8 para encoder)
3. Verifique **configurações de tamanho de texto** não são muito grandes
4. **Apenas caracteres ASCII** - caracteres especiais podem não renderizar
5. Verifique compatibilidade da **versão do firmware**

### Keytimes Não Ciclando

**Problema**: Botão multi-estado não avança estados

**Soluções**:
1. Verifique **keytimes > 1** na configuração
2. Verifique **modo é Toggle ou Select** (não Momentary)
3. Certifique-se **substituições de estado** estão configuradas
4. **Salve configuração** antes de testar
5. Observe **tela do dispositivo** para mudanças de estado

### Aviso de Alterações Não Salvas

**Problema**: Editor avisa sobre alterações não salvas

**Soluções**:
1. **Intencional**: Clique em Salvar para gravar alterações
2. **Falso positivo**: Recarregue para descartar alterações indesejadas
3. **Aviso persistente**: Verifique se algum campo tem erro de validação
4. **Após recarregar**: Aguarde 2-3 segundos para dispositivo reconectar

---

## Suporte e Recursos

- **GitHub Issues**: [Reportar bugs ou solicitar recursos](https://github.com/MC-Music-Workshop/midi-captain-max/issues)
- **Documentação**: [Documentos técnicos](https://github.com/MC-Music-Workshop/midi-captain-max/tree/main/docs)
- **Atualizações de Firmware**: [Últimos lançamentos](https://github.com/MC-Music-Workshop/midi-captain-max/releases)

---

**Copyright © 2026 Maximilian Cascone. Todos os direitos reservados.**
