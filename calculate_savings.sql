WITH prices AS (
	SELECT
	circ_trans.bib_record_hash,
	circ_trans.price

	FROM
	circ_trans

	WHERE
	circ_trans.patron_record_num = 2198439

	GROUP BY
	circ_trans.bib_record_hash,
	circ_trans.price
)

SELECT 
SUM(prices.price) AS total,
(
	SELECT
	MIN(circ_trans.transaction_epoch)
	
	FROM
	circ_trans
	
	WHERE
	circ_trans.patron_record_num = 2198439
) AS min_date

FROM 
prices
;