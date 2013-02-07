
/* show date of first record in api_apilog	*/
select user_id, email, min(inserted) from api_apilog left join auth_user as AU on AU.id=user_id group by user_id, email order by min(inserted);

/* checkins whith software info filled-in	*/
select * from actions_checkin where data like '%software_info":"{%' and data!='{}' and data!='';
