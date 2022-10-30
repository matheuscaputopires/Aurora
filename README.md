# Deve ser um script com abertura pra toolbox

# 1 Buscar no banco de dados uma lista de CNPJs com endereços (CLIENTES) (Variável)
# 1.1 Precisamos de conexão com o banco ou réplica exata dos campos necessários

Quebrar em N cores

# 2 Comparar lista de clientes com feature de clientes geocodificados (Variável)
# 3 Garantir que campo de cliente inativo está atualizado

# 4 Geocodificar quem não está geocodificado e quem teve mudança de endereço
# 5 Em caso de Erro de Geocoding, Erro de Match (Unmatched Addrs), Geocoding na Cidade Errada - Serão armazenados em feature de erros
# 6 Testar geocoding em ceps fora da região apontada

#  Neste ponto, a lista de clientes está pronta
#  Território (Polígono imutável)

# 7 Calcular numero de clientes dentro de cada território
# 8 Logar territórios com mais de X clientes (Variável)

# 9 UM VENDEDOR POR TERRITÓRIO (VENDEDOR) (Variável) Feature com XY dos vendedores, a princípio pode ser o centroide contido do território
# 9.1 A planilha de vendedores tem o horário de atendimento por vendedor (08:00 (12:00 - 13:00) 18:00) 8h totais

Unificar os 8 pedaços em 1
Orquestrar atendimento em semanas, meses, dias da semana ?? (Feature de alto risco)
Distribuir os X territórios em N cores

# 10 Em caso de múltiplas cidades:
  # 10.1: Na Roterização, (Nova funcionalidade)
  #  caso as rotas do vendedor não estejam todas contidas dentro da mesma cidade de origem do vendedor
  #  alocar o vendedor em um pondo de destino diferente do de origem

# 11 Ao alocar uma nova rota, importar também clientes já roterizados e solicitar manter a rota e sequencia original
Exemplo:
  Clientes: 1, 2, 3, 4, 5, 6
  Alocação 1: 0, 3, 4, 2, 6, 0
  Alocação 2: 0, 5, 1, 0
  # Em caso de alteração, recalcular mantendo a ordem original
  Clientes: 2, 4, 5, 6, 7, 8
  Alocação 1: 0, 8, 4, 2, 6, 0
  Alocação 2: 0, 5, 1, 7, 0
# Solução no script do danilo (DANILO) O correto é o que aponta pro SMP

Ao resolver o problema, a cada território, vou exportar para o banco

# Devemos ter todas as alocações já no banco
# Ordem de atendimento com lat e long
# KM rodado na rota total do dia
# Distancia entre clientes
# Directions
