
from fakeidentities.data import NAMES_ALTERNATIVES

if __name__ == '__main__':
    df = NAMES_ALTERNATIVES
    sum_by_name = df.groupby('name').sum().drop(columns='alternative_name').rename(columns={'occurrences': 'sum'})
    print(sum_by_name)
    alt_percent = df.merge(sum_by_name, on='name')
    print(alt_percent)
    alt_percent['%'] = alt_percent['occurrences'] / alt_percent['sum']
    alt_percent = alt_percent.drop(columns=['occurrences', 'sum'])
    print(alt_percent[alt_percent['name'] == 'peter'].sort_values(by=['%'], ascending=False))