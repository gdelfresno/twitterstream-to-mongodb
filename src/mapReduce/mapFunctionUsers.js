function map() {
	var isRT = this.hasOwnProperty('retweeted_status');
	var isReply = this.hasOwnProperty('in_reply_to_screen_name') && this.in_reply_to_screen_name !== null;
	var user = this.user.screen_name;
	if (isRT){
		var rtUser = this.retweeted_status.user.screen_name;
		emit(user, { rt : 0, rtDone : 1, replies : 0, repliesReceived :0 , mentions : 0, mentionsReceived : 0, tweets : 0  });
		emit(rtUser, { rt : 1, rtDone : 0, replies : 0, repliesReceived :0 , mentions : 0, mentionsReceived : 0, tweets : 0  });
		
	} else if (isReply){
		var repliedUser = this.in_reply_to_screen_name;
		emit(user, { rt : 0, rtDone : 0, replies : 1, repliesReceived :0 , mentions : 0, mentionsReceived : 0, tweets : 0  });
		emit(repliedUser, { rt : 0, rtDone : 0, replies : 0, repliesReceived :1 , mentions : 0, mentionsReceived : 0, tweets : 0  });
	}
	
	if (!isRT){
		var mentions = this.entities.user_mentions;
		for (var i = 0; i < mentions.length;i++){
			var mention = mentions[i];
			var mentionUser = mention.screen_name;
			if (mentionUser !== repliedUser){
				emit(user, { rt : 0, rtDone : 0, replies : 0, repliesReceived :0 , mentions : 1, mentionsReceived : 0, tweets : 0  });
				emit(mentionUser, { rt : 0, rtDone : 0, replies : 0, repliesReceived :0 , mentions : 0, mentionsReceived : 1, tweets : 0  });
			}
		}
	}
	
	emit(user, { rt : 0, rtDone : 0, replies : 0, repliesReceived :0 , mentions : 0, mentionsReceived : 0, tweets : 1 });
}