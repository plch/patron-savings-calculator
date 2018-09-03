SELECT
c.id as circ_trans_id,
c.patron_record_id,
r.record_num as patron_record_num,
extract(EPOCH FROM c.transaction_gmt)::INTEGER AS transaction_epoch,
extract(EPOCH FROM c.due_date_gmt)::INTEGER as due_epoch,
c.application_name,
c.stat_group_code_num,
c.loanrule_code_num,
p.bib_level_code,
p.material_code,
c.itype_code_num,
i.price

FROM
sierra_view.circ_trans as c

JOIN
sierra_view.record_metadata as r
ON
  r.id = c.patron_record_id

JOIN
sierra_view.item_record as i
ON
  i.record_id = c.item_record_id

JOIN
sierra_view.bib_record_property as p
ON
  p.bib_record_id = c.bib_record_id

WHERE
c.op_code = 'o'
AND c.id > 1

limit 100