# Notes for installation of this module
In order for this to work properly on the website and actually display the `gln` field, you need to find the ID of the  `gln` field under Settings -> Technical -> Database structure -> Fields

When you have the ID run the following query directly in PostgreSQL

```
UPDATE public.ir_model_fields SET website_form_blacklisted=false WHERE id = <ID of the field>
```

Fx. if the ID is 3711, then the query would be:

```
UPDATE public.ir_model_fields SET website_form_blacklisted=false WHERE id = 3711
```

Restart the Odoo instance now it should be working