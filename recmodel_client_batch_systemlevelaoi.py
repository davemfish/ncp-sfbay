""""
This is a saved model run from natcap.invest.recreation.recmodel_client.
Generated: Mon 28 Nov 2016 09:24:28 AM 
InVEST version: 3.3.1b1.post10+nff1c8fdca089
"""

## USAGE
# python -u recmodel_client_batch_systemlevelaoi.py &> log.txt

import natcap.invest.recreation.recmodel_client
import os

args = {
        u'aoi_path': u'',
        u'grid_aoi': False,
        u'grid_type': u'hexagon',
        u'cell_size': 7000.0,
        u'start_year': u'2010',
        u'end_year': u'2014',
        u'compute_regression': False,
        u'predictor_table_path': u'',
        u'scenario_predictor_table_path': u'',  
        u'results_suffix': u'',
        u'workspace_dir': u'',
}


if __name__ == '__main__':
    BASEDIR = '../data/bcdc_othernaturalareas/System_level_AOIs_Recmodeling/0inches'
    for shpfile in os.listdir(BASEDIR):
        if shpfile.endswith(".shp"):
            args['aoi_path'] = os.path.join(BASEDIR, shpfile)
            workspace = os.path.splitext(shpfile)[0]
            args['workspace_dir'] = os.path.join(BASEDIR, workspace)
            natcap.invest.recreation.recmodel_client.execute(args)
