-- Function: get_price_distribution(integer)

-- DROP FUNCTION get_price_distribution(integer);

CREATE OR REPLACE FUNCTION get_price_distribution(IN p_species_id integer)
  RETURNS TABLE(line_begin numeric, line_end numeric, count bigint) AS
$BODY$
DECLARE min numeric;
DECLARE max numeric;
DECLARE dt numeric;
DECLARE i int;
BEGIN
 select round(min(ebay_item_price),2) as min, round(max(ebay_item_price), 2) as max, (max(ebay_item_price) - min(ebay_item_price))/10 as dt
 INTO min, max, dt
                from species_species ss
                join species_scpecies2item si ON ss.id=si.species_id
                join ebay_parse_ebayitem pe ON pe.ebay_item_id = si.item_id
                WHERE ss.id = p_species_id;
 FOR i IN 1..10 LOOP
	RETURN QUERY select min + dt *(i-1) as line_begin,  min + dt *i as line_end, count(*) 
                from species_species ss
                join species_scpecies2item si ON ss.id=si.species_id
                join ebay_parse_ebayitem pe ON pe.ebay_item_id = si.item_id
                WHERE ss.id = p_species_id 
			AND ebay_item_price BETWEEN min + dt *(i-1) AND min + dt *i;
 END LOOP;
END
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;

