# Introdução
Projeto desenvolvido na linguagem python para criação de uma toolbox do ArcPRO.

Essa toolbox tem como objetivo atualizar os registros de carteiras num feature server do ArcGIS Server referente ao serviço de Roteirização.

Além da atualização da carteira, também é atualizado a listagem de executivos.

# Uso no ArcPRO
Abaixo os passos para utilização da toolbox:
1.	Abrir ArcPRO
2.	Ir na aba Catalog e encontrar o repositório deste projeto
3.	Executar a toolbox LoadWorkArea.tbx
4.	Preencher o formulário com: Feature de Carteira (com os dados novos), Ambiente (que deverá ser atualizado), Usuário e Senha do ambiente do Portal for ArcGIS
5.	Executar o processo da toolbox e aguardar o término

# Instalando Dependencias e Rodando Testes de Unidade
O projeto possui o NPM configurado, dessa forma para rodar os testes deve-se executar os comandos:

`npm pip-install`

`npm run-unit-tests`
