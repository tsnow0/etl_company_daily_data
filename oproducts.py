#!/usr/bin/env python
# coding: utf-8

import DE_GlobalFunctions_Pkg.db as db
from DE_GlobalFunctions_Pkg.DE_Functions import add_first_sale_date


def read_sql(query):
    rcursor = db.storis_read_conn.cursor()
    rcursor.execute(query)

    row = rcursor.fetchone()
    values = []
    while row is not None:
        dict_row = {'oproduct_sku': row[0],
                    'oproduct_description': row[1],
                    'oproduct_description2': row[2],
                    'oproduct_status': row[3],
                    'oproduct_color': row[4],
                    'ogroup_abbrv': row[5],
                    'oproduct_kit_status': row[6],
                    'oproduct_nbr_of_cartons': row[7],
                    'oproduct_pieces_per_carton': row[8],
                    'oproduct_purchase_full_carton': row[9],
                    'oproduct_transfer_full_carton': row[10],
                    'oproduct_default_sell_price': row[11],
                    'oproduct_markdown_price': row[12],
                    'oproduct_sugg_retail_price': row[13],
                    'oproduct_calculated_sell_price': row[14],
                    'oproduct_channels': row[15],
                    'obrand_id': row[16],
                    'oproduct_average_cost': row[17],
                    'oproduct_replacement_cost': row[18],
                    'oproduct_freight_cost': row[19],
                    'oproduct_freight_factor': row[20],
                    'oproduct_freight_factor_indicator': row[21],
                    'oproduct_upc': row[22],
                    'ovendor_id': row[23],
                    'oproduct_vendor_model_id': row[24],
                    'oproduct_is_published_onweb': row[25],
                    'oproduct_is_commissionable': row[26],
                    'oproduct_is_discountable': row[27],
                    'oproduct_is_direct_ship': row[28],
                    'oproduct_is_taxable': row[29],
                    'oproduct_is_special_order': row[30],
                    'oproduct_last_sale_date': row[31],
                    'oproduct_rec_status': row[32],
                    'oproduct_date_created': row[33],
                    'oproduct_date_changed': row[34]}
        values.append(dict_row)
        row = rcursor.fetchone()
    rcursor.close()
    db.storis_read_conn.close()
    return values


########################################################################################
def fix_brand_id(products):
    for prod_dicts in products:
        prod_dicts.update((key, "9999") for key, value in prod_dicts.items() if value == "BeckyOwens")

    return products


########################################################################################
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


########################################################################################
def write_sql(values):
    numchunk = 0
    for chunk in chunker(values, 1000):
        try:
            cursor = db.da_prod_conn.cursor()
            cursor.executemany(insert_query, chunk)
            db.da_prod_conn.commit()
            cursor.close()
            numchunk = numchunk + 1
            print("Chunk #" + str(numchunk) + " - Products Upload")
        except Exception as e:
            print(e)
            print("Chunk #" + str(numchunk) + " - Products Upload Failed")
    db.da_prod_conn.close()


########################################################################################
if __name__ == "__main__":
    read_query = """
                SELECT p.ProductID as oproduct_sku, 
                       p.Description as oproduct_description, 
                       p.Description2 as oproduct_description2,
                       p.PurchaseStatusCodeID as oproduct_status, 
                       p.Color as oproduct_color, 
                       p.GroupID as ogroup_abbrv,
                       p.KitStatus as oproduct_kit_status,
                       p.NbrOfCartons as oproduct_nbr_of_cartons,
                       p.PiecesPerCarton as oproduct_pieces_per_carton,
                       p.PurchaseFullCarton as oproduct_purchase_full_carton,
                       p.TransferFullCarton as oproduct_transfer_full_carton,
                       p.PieceSellPrice as oproduct_default_sell_price, 
                       p.MarkdownPrice as oproduct_markdown_price, 
                       p.SuggRetailPrice as oproduct_sugg_retail_price, 
                       p.CalculatedSellingPrice as  oproduct_calculated_sell_price,
                       CASE WHEN p.CompanyID = '01' THEN 'downeast_home' else p.CompanyID END as oproduct_channels, 
                       p.BrandID as obrand_id, 
                       p.AverageCost as oproduct_average_cost, 
                       p.ReplacementCost as oproduct_replacement_cost, 
                       p.FreightCost as oproduct_freight_cost, 
                       p.FreightFactor as oproduct_freight_factor,
                       p.FreightFactorIndicator as oproduct_freight_factor_indicator,
                       p.UPCNbr as oproduct_upc,
                       p.VendorID as ovendor_id,
                       p.VendorModelNbr as oproduct_vendor_model_id,
                       p.PublishedOnWeb as oproduct_is_published_onweb, 
                       p.Commissionable as oproduct_is_commissionable,
                       p.Discountable as oproduct_is_discountable, 
                       p.IsDirectShipDefault as oproduct_is_direct_ship, 
                       p.Taxable as oproduct_is_taxable, 
                       p.SpecialOrder as oproduct_is_special_order,
                       p.DtLastSold as oproduct_last_sale_date, 
                       p.RecStatus as oproduct_rec_status,
                       p.DateCreated as oproduct_date_created, 
                       p.DateChanged as oproduct_date_changed
                FROM DowneastDW.storis.Product p;
                """

    insert_query = """
                    INSERT INTO oProducts (oproduct_sku, 
                                    oproduct_description,
                                    oproduct_description2, 
                                    oproduct_status,
                                    oproduct_color,
                                    ogroup_abbrv,
                                    oproduct_kit_status,
                                    oproduct_nbr_of_cartons,
                                    oproduct_pieces_per_carton,
                                    oproduct_purchase_full_carton,
                                    oproduct_transfer_full_carton,
                                    oproduct_default_sell_price, 
                                    oproduct_markdown_price,
                                    oproduct_sugg_retail_price,
                                    oproduct_calculated_sell_price,
                                    oproduct_channels,
                                    obrand_id,
                                    oproduct_average_cost,
                                    oproduct_replacement_cost,
                                    oproduct_freight_cost,
                                    oproduct_freight_factor,
                                    oproduct_freight_factor_indicator,
                                    oproduct_upc,
                                    ovendor_id,
                                    oproduct_vendor_model_id,
                                    oproduct_is_published_onweb,
                                    oproduct_is_commissionable,
                                    oproduct_is_discountable,
                                    oproduct_is_direct_ship,
                                    oproduct_is_taxable,
                                    oproduct_is_special_order,
                                    oproduct_last_sale_date,
                                    oproduct_rec_status,
                                    oproduct_date_created,
                                    oproduct_date_changed,
                                    oproduct_first_sale_date
                                    )
                
                    VALUES( %(oproduct_sku)s, 
                            %(oproduct_description)s,
                            %(oproduct_description2)s,
                            %(oproduct_status)s,
                            %(oproduct_color)s,
                            %(ogroup_abbrv)s,
                            %(oproduct_kit_status)s,
                            %(oproduct_nbr_of_cartons)s,
                            %(oproduct_pieces_per_carton)s,
                            %(oproduct_purchase_full_carton)s,
                            %(oproduct_transfer_full_carton)s,
                            %(oproduct_default_sell_price)s, 
                            %(oproduct_markdown_price)s,
                            %(oproduct_sugg_retail_price)s,
                            %(oproduct_calculated_sell_price)s,
                            %(oproduct_channels)s,
                            %(obrand_id)s,
                            %(oproduct_average_cost)s,
                            %(oproduct_replacement_cost)s,
                            %(oproduct_freight_cost)s,
                            %(oproduct_freight_factor)s,
                            %(oproduct_freight_factor_indicator)s,
                            %(oproduct_upc)s,
                            %(ovendor_id)s,
                            %(oproduct_vendor_model_id)s,
                            %(oproduct_is_published_onweb)s,
                            %(oproduct_is_commissionable)s,
                            %(oproduct_is_discountable)s,
                            %(oproduct_is_direct_ship)s,
                            %(oproduct_is_taxable)s,
                            %(oproduct_is_special_order)s,
                            %(oproduct_last_sale_date)s,
                            %(oproduct_rec_status)s,
                            %(oproduct_date_created)s,
                            %(oproduct_date_changed)s,
                            %(oproduct_first_sale_date)s
                            )   
                    ON DUPLICATE KEY UPDATE
                        oproduct_description = VALUES(oproduct_description),
                        oproduct_description2 = VALUES(oproduct_description2),
                        oproduct_status = VALUES(oproduct_status),
                        oproduct_color = VALUES(oproduct_color),
                        ogroup_abbrv = VALUES(ogroup_abbrv),
                        oproduct_kit_status = VALUES(oproduct_kit_status),
                        oproduct_nbr_of_cartons = VALUES(oproduct_nbr_of_cartons),
                        oproduct_pieces_per_carton = VALUES(oproduct_pieces_per_carton),
                        oproduct_purchase_full_carton = VALUES(oproduct_purchase_full_carton),
                        oproduct_transfer_full_carton = VALUES(oproduct_transfer_full_carton),
                        oproduct_default_sell_price = VALUES(oproduct_default_sell_price),
                        oproduct_markdown_price = VALUES(oproduct_markdown_price),
                        oproduct_sugg_retail_price = VALUES(oproduct_sugg_retail_price),
                        oproduct_calculated_sell_price = VALUES(oproduct_calculated_sell_price),
                        oproduct_channels = VALUES(oproduct_channels),
                        obrand_id = VALUES(obrand_id),
                        oproduct_average_cost = VALUES(oproduct_average_cost),
                        oproduct_replacement_cost = VALUES(oproduct_replacement_cost),
                        oproduct_freight_cost= VALUES(oproduct_freight_cost),
                        oproduct_freight_factor = VALUES(oproduct_freight_factor),
                        oproduct_freight_factor_indicator = VALUES(oproduct_freight_factor_indicator),
                        oproduct_upc = VALUES(oproduct_upc),
                        ovendor_id = VALUES(ovendor_id),
                        oproduct_vendor_model_id = VALUES(oproduct_vendor_model_id),
                        oproduct_is_published_onweb = VALUES(oproduct_is_published_onweb),
                        oproduct_is_commissionable = VALUES(oproduct_is_commissionable),
                        oproduct_is_discountable = VALUES(oproduct_is_discountable),
                        oproduct_is_direct_ship = VALUES(oproduct_is_direct_ship),
                        oproduct_is_taxable = VALUES(oproduct_is_taxable),
                        oproduct_is_special_order = VALUES(oproduct_is_special_order),
                        oproduct_last_sale_date = VALUES(oproduct_last_sale_date),
                        oproduct_rec_status = VALUES(oproduct_rec_status),
                        oproduct_date_created = VALUES(oproduct_date_created),
                        oproduct_date_changed = VALUES(oproduct_date_changed),
                        oproduct_first_sale_date = VALUES(oproduct_first_sale_date),
                        OMDT = VALUES(OMDT);
                    """
    print('Products download')
    products = read_sql(read_query)

    # add first sale date to oProducts table
    print('Adding First Sale Date')
    sale_date_query = """
                      SELECT p.oproduct_sku, DATE_FORMAT(MIN(sbc.oSalesByCustomer_date),"%Y-%m-%d") as first_sale_date
                      FROM downeast_analytics.oSalesByCustomer sbc 
                      JOIN downeast_analytics.oProducts p on sbc.oproduct_id = p.oproduct_id
                      GROUP BY sbc.oproduct_id

                         """
    first_sale_dates = add_first_sale_date(sale_date_query)

    for pro_dict in products:
        sku = pro_dict['oproduct_sku']
        fs_date = [fsd_dict['first_sale_date'] for fsd_dict in first_sale_dates if fsd_dict['oproduct_sku'] == sku]
        if len(fs_date) == 0:
            fs_date = [None]
        pro_dict['oproduct_first_sale_date'] = fs_date[0]

    # # fix becky owen products
    # products = fix_brand_id(products)

    # upload updated products
    print('Products Upload')
    write_sql(products)

    print('Products upload finished')
