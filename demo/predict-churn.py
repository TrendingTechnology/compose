# %matplotlib inline
import composeml as cp
import pandas as pd

PARTITION = '100'
BASE_DIR = 's3://customer-churn-spark/'
PARTITION_DIR = BASE_DIR + 'p' + PARTITION
transactions = f'{PARTITION_DIR}/transactions.csv'

transactions = pd.read_csv(
    transactions,
    parse_dates=['transaction_date', 'membership_expire_date'],
    infer_datetime_format=True,
)
transactions.head()


def inactive_membership(transactions):
    if len(transactions) != 2: return

    membership_expire_date = transactions['membership_expire_date']
    membership_expire_date = membership_expire_date.iloc[0]

    next_transaction_date = transactions.index[1]
    inactive = next_transaction_date - membership_expire_date
    return inactive


label_maker = cp.LabelMaker(
    target_entity='msno',
    time_index='transaction_date',
    labeling_function=inactive_membership,
    window_size=2,
)

label_times = label_maker.search(
    transactions,
    minimum_data=0,
    num_examples_per_instance=2,
    gap=1,
    verbose=True,
)
label_times.head()

one_month = pd.Timedelta('31d')
is_churn = label_times.threshold(one_month)
is_churn = is_churn.apply_lead(one_month)
is_churn.head()

is_churn.describe()
is_churn.plot.distribution()