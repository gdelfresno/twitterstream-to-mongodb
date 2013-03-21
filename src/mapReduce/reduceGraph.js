function reduce(key,values) {
	
	var result = { outlinks : [], indegree : 0, outdegree : 0, rts: 0, mts: 0  };
	var arr = [];
	
	
	values.forEach(function(value) {
		if (value.outlinks.length > 0) {
			arr = arr.concat(value.outlinks);
		}
		result.indegree += value.indegree;
      	result.outdegree += value.outdegree;
      	result.rts += value.rts;
      	result.mts += value.mts;
	});
	result.outlinks = arr;
	return result;
}