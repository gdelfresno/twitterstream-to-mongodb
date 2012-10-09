function map() {
	var isRT = this.hasOwnProperty('retweeted_status');
	var isReply = this.hasOwnProperty('in_reply_to_screen_name') && this.in_reply_to_screen_name !== null;
	var user = this.user.screen_name;
	var repliedUser = '';
	if (isRT){
		var rtUser = this.retweeted_status.user.screen_name;
		
		emit(user, { outlinks : [rtUser] , indegree : 0, outdegree: 1 });
		emit(rtUser, { outlinks : [] , indegree : 1, outdegree : 0 });
		
	} else if (isReply){
		var repliedUser = this.in_reply_to_screen_name;
		emit(user, { outlinks : [repliedUser] , indegree : 0, outdegree : 1 });
		emit(repliedUser, { outlinks : [] , indegree : 1, outdegree : 0 });
	}
	
	if (!isRT){
		var mentions = this.entities.user_mentions;
		for (var i = 0; i < mentions.length;i++){
			var mention = mentions[i];
			var mentionUser = mention.screen_name;
			if (mentionUser !== repliedUser){
				emit(user, { outlinks : [mentionUser] , indegree : 0, outdegree : 1 });
				emit(mentionUser, { outlinks : [] , indegree : 1, outdegree : 0 });
			}
		}
	}
	
}