from scripts.capacity_inventory import run

def test_local_capacity_inventory_is_existing_fold_only():
    r=run(); assert len(r['rows'])==24
    for row in r['rows']:
        assert row['fitted_scalars']>0
        assert row['strictly_lower_error_than_presence_mean_samples']+row['strictly_higher_error_samples']<=row['samples']
        if row['model']=='presence_mean':
            assert row['fitted_scalars']==row['taxa'] and row['gradient_epochs']==0
        elif row['model']=='cnode':
            assert row['fitted_scalars']==row['taxa']**2
        elif row['model']=='glv':
            assert row['fitted_scalars']==row['taxa']**2+row['taxa']
    assert 'no matched-budget' in r['scope']
