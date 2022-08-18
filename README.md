# Authentium


## API Information

### Permission API

- Provide initial permission data:

```
python manage.py loaddata permissions.json
```

- Get permission data:

```
GET: http://[HOST]:8000/api/permissions

Example response:
{
    "data": [
        {
            "id": 1,
            "name": "oms-trading:*",
            "description": "Trading | All the trading permissions"
        },
        {
            "id": 2,
            "name": "oms-account:*",
            "description": "Account Data | All the account permissions"
        },
        ...
    ]
}

You can update Permission data from Exberry by "update" parameter:
- "update": "true" or "false" (default is "false")
```

### Account API

- Create account and save it to Authentium database:

```
POST: http://[HOST]:8000/api/accounts

Example request: 
{
    "name": "Account1",
    "status": "Pending"
}
```

- Update account and save it to Authentium database:

```
PATCH: http://[HOST]:8000/api/accounts/{id}

Example request:
{
    "name": "Account1",
    "status": "Pending"
}
```

- Get account with id:

```
GET: http://[HOST]:8000/api/accounts/{id}

Example response:
{
    "id": "5470acfd-2678-4ba0-b656-c62ca17d9d21",
    "account_id": "2fd53d94-cc72-4bc4-a3b8-1aaffb1a3f59",
    "name": "Account33",
    "ledger_system": "Algorand",
    "ledger_account_id": "WMJCDVMQTBTYXEOGR7ESY2I4SZ7SFLLT6RPQUBQMRYRCRUSO3MXVIS3TK4",
    "oms_account_id": "40",
    "assets": [],
    "comp_id": "",
    "fees": []
}
```

- Get all account:

```
GET: http://[HOST]:8000/api/accounts

You can specify pagination GET parameters:
- "page": [number of page]
- "data_per_page": [number of data per page]

When you query all, the output will look like this:

[
    {
        "id": "113d4532-18f3-40b8-ad87-08c9efbda9f2",
        "account_id": "9ff1a0dc-d0cc-4070-9e8d-c4472b74eb6a",
        "name": "Account40",
        "status": "Pending",
        "ledger_system": "Algorand",
        "ledger_account_id": "B3STWUZZPHOIUA7OOCF2ZMTWNUYOSNCDLTI4WRW7EAWQV3Q6EV6KYIQR5I",
        "oms_account_id": "47",
        "assets": [],
        "comp_id": "",
        "fees": []
    },
    {
        "id": "329d0146-f686-4698-9213-310ed032f218",
        "account_id": "a1c4cca4-fa64-4c5c-852f-232c18686fc5",
        "name": "Account39",
        "status": "Pending",
        "ledger_system": "Algorand",
        "ledger_account_id": "ULFD5MJ3FEBDE5AA4I5U5VF2ZJZWZ53ZHELOPWHLUX6QW4WQC3E4H24Q6U",
        "oms_account_id": "46",
        "assets": [],
        "comp_id": "",
        "fees": []
    },
        ...
]
```
