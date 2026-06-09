inventory_query = '''
                        SELECT pro.oproduct_id,
                               ih.oinv_date                                                             as InvDate,
                               SUM(ih.oinv_on_hand)                                                     as TotalOnHand 
                        FROM new_db.oInventoryHistory ih
                          JOIN new_db.oProducts pro on ih.oproduct_sku = pro.oproduct_sku
                          JOIN (SELECT YEAR(i.oinv_date),
                                       MONTH(i.oinv_date),
                                       MAX(i.oinv_date) as maxdate
                                FROM new_db.oInventoryHistory i
                                WHERE YEAR(i.oinv_date) > 2019
                                GROUP BY YEAR(i.oinv_date), MONTH(i.oinv_date)
                            ) x on ih.oinv_date = x.maxdate                                              
                        WHERE ih.ostore_id = 1904                                                        
                           AND ih.oinv_date >= %s - INTERVAL 365 DAY                              #only look at inventory for last 365 days
                           AND ih.oinv_date < %s                                                  #dont include todays inventory
                        GROUP BY pro.oproduct_id, ih.oinv_date
                      '''

revenue_query = '''
                    SELECT  sbc.oproduct_id,
                            sbc.okit_status as KitStatus,
                            ROUND(sum(sbc.oSalesByCustomer_amount),4)                                      as Rev,
                            ROUND(SUM(sbc.oSalesByCustomer_units),0)                                       as Units
                     FROM new_db.oSalesByCustomer sbc
                      JOIN new_db.oProducts pro on sbc.oproduct_id = pro.oproduct_id
                     WHERE sbc.oSalesByCustomer_date >= %s - INTERVAL 365 DAY                       #only look at sales for last 365 days
                       AND sbc.oSalesByCustomer_date < %s                                           #dont include todays sales
                     GROUP BY sbc.oproduct_id,sbc.okit_status
                '''

products_query = '''
            SELECT p.oproduct_id,
                   p.oproduct_sku as SKU,
                   p.oproduct_description as Description,
                   p.oproduct_status as Status,
                   p.oproduct_first_sale_date as FSD,
                   p.oproduct_last_sale_date as LSD,
                   p.oproduct_replacement_cost as ReplacementCost,
                   v.ovendor_freight_factor as FreightFactor,
                   g.ocategory_abbrv as Category,
                   g.ogroup_abbrv as 'Group'
            FROM new_db.oProducts p
            JOIN new_db.oGroups g on p.ogroup_abbrv = g.ogroup_abbrv
            JOIN new_db.oVendors v on p.ovendor_id = v.ovendor_id
            WHERE g.ocategory_abbrv NOT IN ('OTHER','DONATE','CONSIG','AR','MS','DA','LT','SE',    
                          'FIXTUR','WR','WA','GIFT','SAMPL','RUG','SUPPLY', 'CONSUM')              
            AND g.ogroup_abbrv NOT IN ('ODACCS')                                                   
            AND p.oproduct_rec_status <> 'D'                                                        
            '''

kit_query = '''
            SELECT kc.oproduct_id,
                   kc.okit_product_id,
                   kc.okit_component_qty as CompQty
            FROM new_db.oKitComponents kc
            WHERE kc.okit_component_recstatus <> 'D'
            '''

castlegate_inv_snapshot = """
        SELECT
            p.oproduct_sku AS 'Part Number',
            SUM(i.oinventory_available) AS 'Total Available',
            c.ocost_amount AS 'Per Unit $',
            SUM(i.oinventory_available) * c.ocost_amount AS Total
            FROM hq.oinventory i
            JOIN hq.oproducts p ON i.oproduct_id = p.oproduct_id
            LEFT JOIN hq.ocosts c ON i.oproduct_id = c.oproduct_id AND c.ocost_type = 'landed_cost'
            WHERE i.olocation_id = 5
        GROUP BY i.oproduct_id, p.oproduct_sku
        HAVING SUM(i.oinventory_available) > 0;
    """
