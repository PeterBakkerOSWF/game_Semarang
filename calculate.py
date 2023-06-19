from beslissingen import production as pr, sales as sa, development as de, asset_recovery as asset
from parameters import ar, compliance, designer, builder, coll_raticum, delta, dev_footprint, end_customer
from parameters import investment_cost, seller, time_to_market, yield_reman
import numpy as np

ronde = []
kpi_round_result = []
executed = False
x = 1
while x <= 4:

    production = pr
    development = de
    sales = sa
    asset_recovery = asset

    if x == 3:
        production = [1, 1, 1, 0]

    if x == 4:
        sales = [1, 0, 1, 1]

    x += 1

    d_eco_quality_mgt_cost = investment_cost[3] * asset_recovery[2]
    d_market_sales_volume_reman = max(end_customer[4], end_customer[4] * end_customer[5] * production[3]) * production[
        2]
    d_circular_yield = yield_reman[4] * asset_recovery[2] + yield_reman[7] * development[1] + yield_reman[10] * \
                       development[2]
    d_circular_yield += yield_reman[13] * development[3]
    d_circular_yield = max(d_circular_yield, 0.01)
    d_circular_collection_rate = coll_raticum[1] + coll_raticum[4] * asset_recovery[0] + coll_raticum[7] * sales[2]
    d_circular_collection_rate += coll_raticum[10] * sales[3] + coll_raticum[13] * development[3]

    d_market_sales_volumes_new = max(end_customer[1], end_customer[1] * end_customer[2] * production[3])
    d_market_sales_volumes_new -= delta[4] * sales[0] * end_customer[1] * production[1]
    d_market_total_volume = d_market_sales_volume_reman + d_market_sales_volumes_new
    d_circular_reuse_rate = d_market_sales_volume_reman / d_market_total_volume * 100

    d_eco_production_cost_new = production[1] * builder[3] * d_market_sales_volumes_new
    d_market_cannibalisation_volume = d_market_total_volume * (
            end_customer[7] / 100 - delta[1] * sales[2] - delta[2] * sales[1])
    d_eco_turnover = d_market_sales_volume_reman * end_customer[15] + end_customer[13] * d_market_sales_volumes_new
    d_eco_turnover -= d_market_cannibalisation_volume * (end_customer[13] + end_customer[15] / 2)

    d_market_volume_collected_products = d_circular_collection_rate / 100 * d_market_total_volume
    d_market_volume_cores_reman_internal = d_market_volume_collected_products * d_circular_yield * production[2]
    d_market_volume_cores_reman_internal *= (1 - asset_recovery[1])
    reman_internal = d_market_sales_volume_reman - d_market_volume_cores_reman_internal
    d_market_volume_cores_reman_external_buy = max(0, reman_internal / d_circular_yield)
    d_market_volume_recycled_materials_intern = d_market_volume_collected_products - d_market_volume_cores_reman_internal
    volume_new_rec = d_market_sales_volumes_new - d_market_volume_recycled_materials_intern
    d_market_volume_recycled_materials_external = max(0, volume_new_rec * production[0])
    d_market_volume_virgin_material_external = d_market_total_volume - d_market_volume_recycled_materials_external
    d_market_volume_virgin_material_external -= d_market_volume_recycled_materials_intern

    d_circular_recycle_rate = (
            production[0] * 100 * d_market_volume_recycled_materials_external / d_market_total_volume)
    d_circular_recycle_rate += d_market_volume_recycled_materials_intern / d_market_total_volume * 100
    d_circular_total_recovery = (d_circular_reuse_rate + d_circular_recycle_rate) * d_circular_collection_rate / 100
    virgin = d_market_total_volume - d_market_volume_recycled_materials_external - d_market_volume_recycled_materials_intern
    d_eco_sourcing_cost_virgin = virgin * builder[1]
    volume_recyc = d_market_volume_recycled_materials_intern * builder[5]
    volume_recyc += d_market_volume_recycled_materials_external * builder[9]
    d_eco_sourcing_cost_recycle = production[0] * volume_recyc
    d_eco_production_cost_reman = production[2] * builder[7] * d_market_sales_volume_reman
    d_eco_production_cost_reman += d_market_volume_cores_reman_external_buy * builder[11]
    d_eco_distribution_cost = d_market_total_volume * seller[1]

    d_eco_asset_recovery_processing_cost = (
            d_market_volume_collected_products * d_circular_yield * ar[10] * ar[11] * ar[12])
    d_eco_asset_recovery_processing_cost += (
            d_market_volume_collected_products * (1 - d_circular_yield) * ar[3] * ar[4] * ar[5])
    d_eco_collection_cost = (ar[1] * (1 - asset_recovery[0]) + asset_recovery[0] * ar[
        8]) * d_market_volume_collected_products
    d_eco_it_cost = development[3] * investment_cost[3] + production[3] * investment_cost[5]
    d_eco_it_cost += asset_recovery[3] * investment_cost[7]
    d_eco_development_cost = designer[1] * development[0] + development[1] * designer[3] + designer[5] * development[2]
    d_eco_capital_cost_cbm = sales[2] * investment_cost[1] * 0.12
    d_eco_penalty_non_compliance_ar = 0

    if d_circular_collection_rate < 70:
        d_eco_penalty_non_compliance_ar += coll_raticum[20]
    if d_circular_reuse_rate + d_circular_recycle_rate < 80:
        d_eco_penalty_non_compliance_ar += yield_reman[23]

    d_leadtime_to_market = time_to_market[1] * development[0] + development[1] * time_to_market[9]
    d_leadtime_to_market += time_to_market[17] * development[2]
    d_leadtime_new_sc_virgin_weeks = time_to_market[3] * production[1] + production[1] * time_to_market[5]
    d_leadtime_new_sc_virgin_weeks += time_to_market[7] + production[3] * time_to_market[6]
    d_leadtime_new_sc_recycled_weeks = time_to_market[3] * production[0] + (1 - production[0]) * time_to_market[3]
    d_leadtime_new_sc_recycled_weeks += time_to_market[5] * production[1] + time_to_market[7]
    d_leadtime_new_sc_recycled_weeks += production[3] * time_to_market[6] + asset_recovery[3] * yield_reman[17]

    d_leadtime_collection_weeks = coll_raticum[2] * (1 - asset_recovery[0]) + asset_recovery[0] * coll_raticum[5]
    d_leadtime_collection_weeks += coll_raticum[8] * sales[2] + development[3] * coll_raticum[14]
    d_leadtime_collection_weeks += coll_raticum[11] * sales[3]
    d_leadtime_sc_reman_incl_coll_weeks = d_leadtime_collection_weeks + yield_reman[2] + yield_reman[17] * \
                                          asset_recovery[3]
    d_leadtime_sc_reman_incl_coll_weeks += production[3] * time_to_market[19]

    d_carbon_footprint_use = end_customer[9] * d_market_sales_volumes_new + d_market_sales_volume_reman * end_customer[
        11]
    d_carbon_footprint_ar = (d_market_volume_cores_reman_internal + d_market_volume_cores_reman_external_buy)
    d_carbon_footprint_ar *= coll_raticum[16] * (1 - asset_recovery[0])
    reman = d_market_volume_cores_reman_internal + d_market_volume_cores_reman_external_buy
    d_carbon_footprint_ar += reman * asset_recovery[0] * coll_raticum[18]
    recycled = d_market_volume_recycled_materials_external + d_market_volume_recycled_materials_intern
    d_carbon_footprint_ar += yield_reman[19] * recycled
    d_carbon_footprint_ar += yield_reman[21] * reman
    d_carbon_footprint_distribution = d_market_total_volume * dev_footprint[6]

    d_carbon_footprint_production = d_market_volume_cores_reman_internal * dev_footprint[12]
    d_carbon_footprint_production += dev_footprint[18] * d_market_volume_cores_reman_external_buy
    d_carbon_footprint_production += d_market_sales_volumes_new * dev_footprint[5]
    d_carbon_footprint_production += d_market_volume_cores_reman_external_buy
    d_carbon_footprint_sourcing = d_market_volume_virgin_material_external * dev_footprint[3]
    d_carbon_footprint_sourcing += dev_footprint[10] * d_market_volume_recycled_materials_intern
    d_carbon_footprint_sourcing += d_market_volume_recycled_materials_external * dev_footprint[16]
    d_carbon_footprint_development = development[0] * dev_footprint[1] + development[1] * dev_footprint[8]
    d_carbon_footprint_development += development[2] * dev_footprint[14]
    carbon = d_carbon_footprint_use + d_carbon_footprint_ar + d_carbon_footprint_distribution / 1000
    d_carbon_footprint_co2 = carbon + d_carbon_footprint_production / 1000
    d_carbon_footprint_co2 += (d_carbon_footprint_sourcing + d_carbon_footprint_development) / 1000
    d_carbon_total_footprint = d_carbon_footprint_co2 / d_market_total_volume

    d_eco_carbon_fee = d_carbon_footprint_co2 * compliance[1]
    d_eco_total_cost = d_eco_sourcing_cost_virgin + d_eco_sourcing_cost_recycle + d_eco_production_cost_reman
    d_eco_total_cost += d_eco_production_cost_new
    d_eco_total_cost += d_eco_distribution_cost + d_eco_asset_recovery_processing_cost + d_eco_collection_cost
    d_eco_total_cost += d_eco_quality_mgt_cost + d_eco_it_cost
    d_eco_total_cost += d_eco_development_cost + d_eco_capital_cost_cbm + d_eco_penalty_non_compliance_ar + d_eco_carbon_fee
    d_eco_profit = d_eco_turnover - d_eco_total_cost
    d_eco_gross_margin = d_eco_profit / d_eco_turnover * 100
    d_eco_after_tax = d_eco_gross_margin * 0.6

    score_team_ronde = [["turnover", int(d_eco_turnover)], ["Total cost", int(d_eco_total_cost)],
                        ["profit", int(d_eco_profit)],
                        ["gross margin", int(d_eco_gross_margin)], ["CO2/ton", int(d_carbon_footprint_co2)],
                        ["footprint incl use", int(d_carbon_footprint_use)],
                        ["total recovery", int(d_circular_total_recovery)],
                        ["footprint p product", int(d_carbon_total_footprint)], ["IT-cost", int(d_eco_it_cost)],
                        ["carbon fee", int(d_eco_carbon_fee)], ["after tax", int(d_eco_after_tax)],
                        ["production", int(d_carbon_footprint_production)],
                        ["development", int(d_carbon_footprint_development)],
                        ["after tax", int(d_eco_after_tax)], ["Reuserate", int(d_circular_reuse_rate)],
                        ["recycle rate", int(d_circular_recycle_rate)],
                        ["collection rate", int(d_circular_collection_rate)],
                        ["total volume", int(d_market_total_volume)],
                        ["cannibalisation", int(d_market_cannibalisation_volume)],
                        ["collected volume", int(d_market_volume_collected_products)],
                        ["reman internal volume", int(d_market_volume_cores_reman_internal)],
                        ["reman external; buy", int(d_market_volume_cores_reman_external_buy)],
                        ["time to market", int(d_leadtime_to_market)],
                        ["leadtime new SC virgin", int(d_leadtime_new_sc_virgin_weeks)],
                        ["leadtime new recycled", int(d_leadtime_new_sc_recycled_weeks)],
                        ["leadtime collection", int(d_leadtime_collection_weeks)],
                        ["leadtime SC reman incl coll", int(d_leadtime_sc_reman_incl_coll_weeks)],
                        ["Gross margin", int(d_eco_gross_margin)]]

    # print(score_team_ronde)
    kpi = [["turnover", int(d_eco_turnover)], ["total_cost", int(d_eco_total_cost)], ["profti", int(d_eco_profit)],
           ["margin", int(d_eco_gross_margin)], ["recovery", int(d_circular_total_recovery)],
           ["footprint", int(d_carbon_total_footprint)]]

    if not executed:
        results = np.array(score_team_ronde)
        ronde = score_team_ronde
        kpi_round_rersult = kpi
        executed = True

    ronde = ronde + score_team_ronde
    kpi_round_result = kpi_round_result + kpi

team_results = results
ronde_results = np.array(ronde)
kpi_present = np.array(kpi_round_result)
