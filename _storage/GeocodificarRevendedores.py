# coding: utf-8

import arcpy
import utils

arcpy.env.overwriteOutput = True

### Helper Functions ###


### Main Function ###
revendedores_fc = arcpy.GetParameterAsText(0)
BRA_locator = arcpy.GetParameterAsText(1)

if not revendedores_fc:
    revendedores_fc = r'D:\projetos\boticario\Boticario.gdb\Base_Revendedores'
    BRA_locator = r"D:\bases\SMP\NewLocators\BRA\BRA.loc"

arcpy.Delete_management('in_memory')
arcpy.Delete_management('%scratchGDB%')

arcpy.AddMessage('Iniciando geocodificação de revendedores')

## Geocodificar por endereços:
geocode_fc = '%scratchGDB%/revendedores_pendentes_geocode_addr'
# geocode_fc = r'D:\projetos\boticario\Boticario.gdb\revendedores_pendentes_geocode_addr'

revendedores_select = arcpy.SelectLayerByAttribute_management(revendedores_fc, "NEW_SELECTION", "GEOCODE = 1", None)
revendedores_pendentes = arcpy.CopyRows_management(revendedores_select, 'in_memory/revendedores_pendentes')
arcpy.AddMessage('Geocodificando {} endereços...'.format(arcpy.GetCount_management(revendedores_pendentes)))
geocode_result = arcpy.geocoding.GeocodeAddresses(revendedores_pendentes, BRA_locator, "'Address or Place' DS_RUA_RESIDENCIAL VISIBLE NONE;Address2 NR_NUMERO_RESIDENCIAL VISIBLE NONE;Address3 <None> VISIBLE NONE;Neighborhood DS_BAIRRO_RESIDENCIAL VISIBLE NONE;City DS_CIDADE_RESIDENCIAL VISIBLE NONE;Subregion <None> VISIBLE NONE;State DS_ESTADO VISIBLE NONE;ZIP NR_CEP_RESIDENCIAL VISIBLE NONE;ZIP4 <None> VISIBLE NONE;Country <None> VISIBLE NONE", geocode_fc, "STATIC", None, "ROUTING_LOCATION", "Subaddress;'Point Address';'Street Address';'Distance Marker';Intersection;'Street Name';'Primary Postal';'Postal Locality';'Postal Extension'")
if geocode_result.status == 4:  #Succeeded
    arcpy.AddMessage(geocode_result.getMessage(2))
    arcpy.AddMessage(geocode_result.getMessage(3))
    arcpy.AddMessage(geocode_result.getMessage(4))
    arcpy.AddMessage(geocode_result.getMessage(5))

arcpy.AddMessage('Calculando endereços geocodificados fora da cidade correta')
num = utils.compara_cep_geocode(geocode_fc)
arcpy.AddMessage('Reexecutando geocodificação para {} endereços com problemas'.format(num))
geocode_result = utils.rematch_por_cep(geocode_fc)

## Atualizar shapes
updated = 0
arcpy.AddMessage('Atualizando localizações na base ativa')
with arcpy.da.SearchCursor(geocode_fc, ['SHAPE@XY', 'USER_CD_PESSOA']) as reader:
    for input_row in reader:
        with arcpy.da.UpdateCursor(revendedores_fc, ['SHAPE@XY', 'GEOCODE'],
                                                "CD_PESSOA = {}".format(input_row[1])) as updater:
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
arcpy.AddMessage('Geocodificação de revendedores concluída com sucesso!')
