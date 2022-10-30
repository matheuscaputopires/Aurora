# coding: utf-8

import arcpy

## Comparar 3 primeiros dígitos do CEP geocodificado (Postal) com o CEP de entrada (IN_Postal) para saber se a geocodificação caiu na região correta
## Caso tenha caido na regiao errada, é criado um campo rematch com valor true
def compara_cep_geocode(fc):
    errados = 0
    arcpy.management.AddField(fc, "Rematch", "SHORT", None, None, 3, '', "NULLABLE", "NON_REQUIRED", '')
    with arcpy.da.UpdateCursor(fc, ['Rematch', 'Postal', 'IN_Postal']) as updater:
        for row in updater:
            cep_geocode = row[1]
            cep_user = row[2]
            if cep_user is not None and len(cep_user) >= 3:
                if cep_geocode is None: ## nao veio cep (provavelmente nao geocodificou)
                    row[0] = True
                    updater.updateRow(row)
                    errados += 1
                else:
                    cep_user_3 = cep_user[:3]
                    cep_geocode_3 = cep_geocode[:3] if len(cep_geocode) >= 3 else None
                    if cep_geocode_3 != cep_user_3: ## geocodificou em área diferente
                        row[0] = True
                        updater.updateRow(row)
                        errados += 1
    return errados


def rematch_por_cep(fc):
    ## Rematch dos endereços
    result = arcpy.geocoding.RematchAddresses(fc, "Rematch = 1")
    arcpy.DeleteField_management(fc, "Rematch")
    # arcpy.CalculateField_management(geocode_fc, 'Rematch', expression="None", expression_type="PYTHON3")
    return result
