function reduce(key,values) {
	var result =  { rt : 0, rtDone : 0, replies : 0, repliesReceived :0 , mentions : 0, mentionsReceived : 0, tweets : 0  };
	
	values.forEach(function(value) {
	      result.rt += value.rt;
	      result.rtDone += value.rtDone;
	      result.replies += value.replies;
	      result.repliesReceived += value.repliesReceived;
	      result.mentions += value.mentions;
	      result.mentionsReceived += value.mentionsReceived;
	      result.tweets += value.tweets;
		});
	return result;
}