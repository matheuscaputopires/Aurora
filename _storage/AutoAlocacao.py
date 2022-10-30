import arcpy
import os
import csv
import datetime 
from datetime import datetime, date, time, timedelta
import string
import random

input_xls = arcpy.GetParameter(0)
Clientes_fc = arcpy.GetParameter(1)
BRA_locator = arcpy.GetParameter(2)
territorios = arcpy.GetParameter(3)
inNetworkDataset = arcpy.GetParameter(4)
BancoPrincipal = arcpy.GetParameter(5)
PastaDeRotas = arcpy.GetParameter(6)
PastaDeSaida = arcpy.GetParameter(7)

arcpy.env.overwriteOutput = True


#Atualização da Base
arcpy.Delete_management('in_memory')
arcpy.Delete_management('%scratchGDB%')

arcpy.AddMessage('Iniciando atualização da base de Clientes...')

tabelaclientes = arcpy.ExcelToTable_conversion(input_xls, 'in_memory/tabelaclientes')

arcpy.AddMessage('Atualizando base de clientes ativos...')
arcpy.AddMessage('Atualizando registros existentes')
updated = 0
rows_to_insert = []
source_fields = ['CNPJ_CLIE', 'ENDERECO_CLIE', 'NRO_ENDERECO_CLIE', 'BAIRRO_CLIE', 'CIDADE_CLIE', 'ESTADO_CLIE',
        'SITUACAO', 'SITUACAO_RECEITA', 'SITUACAO_SINTEGRA', 'SITUACAO_SUFRAMA', 'LATITUDE', 'LONGITUDE']
target_fields = ['CNPJ_CLIE', 'ENDERECO_CLIE', 'NRO_ENDERECO_CLIE', 'BAIRRO_CLIE', 'CIDADE_CLIE', 'ESTADO_CLIE',
        'SITUACAO', 'SITUACAO_RECEITA', 'SITUACAO_SINTEGRA', 'SITUACAO_SUFRAMA', 'LATITUDE', 'LONGITUDE', 'GEOCODE']
with arcpy.da.SearchCursor(tabelaclientes, source_fields) as reader:
    for input_row in reader:
        with arcpy.da.UpdateCursor(Clientes_fc, target_fields, "CNPJ_CLIE = '{}'".format(str(input_row[0]))) as updater:
            new_row = []
            for idx in range(len(source_fields)):
                new_row.append(input_row[idx])
            row = next(updater, None)
            if row:
                idx_geocode = len(source_fields)
                geocodificar = row[idx_geocode]
                if not geocodificar:
                    for i in range(1,5):  # campos de endereço
                        if row[i] != new_row[i]:
                            geocodificar = True;
                new_row.append(geocodificar)
                updater.updateRow(new_row)
                updated += 1
            else:
                new_row.append(True) # Geocode
                rows_to_insert.append(new_row)

arcpy.AddMessage('{} registros atualizados'.format(updated))
arcpy.AddMessage('Inserindo novos registros')

with arcpy.da.InsertCursor(Clientes_fc, target_fields) as inserter:
    for row in rows_to_insert:
        inserter.insertRow(row)

arcpy.AddMessage('{} registros inseridos'.format(len(rows_to_insert)))
arcpy.Delete_management('in_memory')
arcpy.Delete_management('%scratchGDB%')



# Geocodificação


arcpy.env.overwriteOutput = True
arcpy.Delete_management('in_memory')
arcpy.Delete_management('%scratchGDB%')

#Variáveis para Geocodificação
address_fields = "'Address' ENDERECO_CLIE VISIBLE NONE;Neighborhood BAIRRO_CLIE VISIBLE NONE;City CIDADE_CLIE VISIBLE NONE;Region ESTADO_CLIE VISIBLE NONE;POSTAL <None> VISIBLE NONE"


arcpy.AddMessage('Iniciando geocodificação de clientes')

## Geocodificar por endereços:
geocode_fc = '%scratchGDB%/clientes_pendentes_geocode_addr'

arcpy.MakeFeatureLayer_management (Clientes_fc, "Clientes")
clientes_select = arcpy.SelectLayerByAttribute_management("Clientes", "NEW_SELECTION", "GEOCODE = '1'")
clientes_pendentes = arcpy.CopyRows_management(clientes_select, 'in_memory/clientes_pendentes')
arcpy.AddMessage('Geocodificando {} endereços...'.format(arcpy.GetCount_management(clientes_pendentes)))
geocode_result = arcpy.geocoding.GeocodeAddresses(clientes_pendentes, BRA_locator, address_fields, geocode_fc, "STATIC", None, "ROUTING_LOCATION")
if geocode_result.status == 4:  #Succeeded
    arcpy.AddMessage(geocode_result.getMessage(2))
    arcpy.AddMessage(geocode_result.getMessage(3))
    arcpy.AddMessage(geocode_result.getMessage(4))
    arcpy.AddMessage(geocode_result.getMessage(5))

updated = 0
arcpy.AddMessage('Atualizando localizações na base ativa')
with arcpy.da.SearchCursor(geocode_fc, ['SHAPE@XY', 'CNPJ_CLIE']) as reader:
    for input_row in reader:
        with arcpy.da.UpdateCursor("Clientes", ['SHAPE@XY', 'GEOCODE'], "CNPJ_CLIE = '{}'".format(str(input_row[1]))) as updater:
            row = next(updater, None)
            if row:
                row[0] = input_row[0]
                row[1] = None
                updater.updateRow(row)
                updated += 1

arcpy.AddMessage('{} registros atualizados'.format(updated))

arcpy.Delete_management(geocode_fc)
arcpy.Delete_management('in_memory')
arcpy.Delete_management('%scratchGDB%')
arcpy.AddMessage('Geocodificação de clientes concluída com sucesso!')


#Conta o numero de territorios
count = 0
territories = []
for row in arcpy.da.SearchCursor(territorios, field_names=['TerrOID'], sql_clause=('DISTINCT',None)):
    if row[0] > 0:
        count = count +1
        values = count
        territories.append(values)
    
# Separa os Clientes Por território
arcpy.MakeFeatureLayer_management(Clientes_fc, "Clientes")
arcpy.MakeFeatureLayer_management(territorios, "Territorios_lyr")
arcpy.env.workspace = BancoPrincipal
# Dentro da seleção faça uma subseleção baseada em um atributo
for territorio in territories:
    expression = ("TerrName = 'Territory "+  str(territorio) + "'" )
    expression2 = ("SITUACAO = 'ATIVO'" )
    arcpy.AddMessage(expression)
    TerritorioSelecionado = arcpy.SelectLayerByAttribute_management('Territorios_lyr', 'NEW_SELECTION', expression)
    #Selecione as informações que estão em uma determinada região 
    arcpy.SelectLayerByLocation_management('Clientes', 'intersect', TerritorioSelecionado, 0, 'NEW_SELECTION')
    arcpy.SelectLayerByAttribute_management('Clientes', 'SUBSET_SELECTION', expression2)
    # Se existirem feições grave em uma nova feature class
    matchcount = int(arcpy.GetCount_management("Clientes")[0]) 
    if matchcount == 0:
        arcpy.AddMessage('Nenhum dado selecionado')
    else:
        NomeArquivo = ("Clientes_Territorio_" + str(territorio)) 
        arcpy.CopyFeatures_management("Clientes", NomeArquivo)
        arcpy.AddMessage('{0} clientes selecionados de {0}'.format(matchcount, NomeArquivo))


mxd = arcpy.mapping.MapDocument('CURRENT')
mxd_path = os.path.dirname(mxd.filePath) 
arcpy.env.workspace = PastaDeRotas
count2 = 0
busca = '*.' + 'lyr'
if len(arcpy.ListFiles(busca)) > 0:
    for arquivo in arcpy.ListFiles(busca):
        count2 = count2 + 1
        #Criar as rotas
        arcpy.AddMessage("Roteirizando "+ arquivo)
        #Check out the Network Analyst extension license
        arcpy.CheckOutExtension("Network")

        #Set local variables
        df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
        Layer1 = arquivo 
        addLayer = arcpy.mapping.Layer(Layer1)
        arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")

        #Variaveis PAra a rota
        outNALayer = "Vehicle Routing Problem"
        outNALayerName = arquivo
        impedanceAttribute = "TravelTime"
        distanceAttribute = "Kilometers"
        timeUntis = "Minutes"
        distanceUntis = "Kilometers"
        inOrders = str(BancoPrincipal) + "\Clientes_Territorio_{}".format(count2)
        outLayerFile = str(PastaDeSaida) +"\\" + outNALayer + "{}_atualizado.lyr".format(count2)


        #Load the store locations as orders. Using field mappings we map the 
        #TimeWindowStart1, TimeWindowEnd1 and DeliveryQuantities 
        #properties for Orders from the fields of store features and assign a value
        #of 0 to MaxViolationTime1 property. The Name and ServiceTime properties have
        #the correct mapped field names when using the candidate fields from store
        #locations feature class.

        NaLayer = arcpy.mapping.Layer(outNALayer)
        candidateFields = arcpy.ListFields(inOrders)
        ordersSubLayerName = arcpy.na.GetNAClassNames(NaLayer)["Orders"]

        orderFieldMappings = arcpy.na.NAClassFieldMappings(NaLayer, ordersSubLayerName, False, candidateFields)
        orderFieldMappings["Name"].mappedFieldName = "CNPJ_CLIE"
        arcpy.na.AddLocations (NaLayer, ordersSubLayerName, inOrders, orderFieldMappings,"","","", "MATCH_TO_CLOSEST", "CLEAR")

        #Solve the VRP layer
        arcpy.na.Solve(NaLayer)
    
        #Save the solved VRP layer as a layer file on disk with relative paths
        arcpy.management.SaveToLayerFile(NaLayer, outLayerFile, "RELATIVE")

        arcpy.AddMessage("Limpando área de trabalho")
        arcpy.Delete_management(NaLayer)

arcpy.AddMessage("Script completed successfully")

