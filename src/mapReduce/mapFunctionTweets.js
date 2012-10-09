function map() {
	var isRT = this.hasOwnProperty('retweeted_status');
	if (isRT){
		var tweet = this.retweeted_status.id_str;
		emit(tweet, 1);
	} 
}