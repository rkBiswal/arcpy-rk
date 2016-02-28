--For Enterprise Geodatabase, just update the shape column in the GDB_Items table.
--It would be really easy to just update that table... but probably not a supported workflow.
--Feature Classes that don't have extent information.  
-- In ArcGIS 10.4

select name, sde.st_astext(shape) from gdb_items  
where shape is null or dbms_lob.compare(sde.st_astext(shape), 'POLYGON EMPTY') = 0  
