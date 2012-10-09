function reduce(key,values){
	var result = 0;
	values.forEach(function(value) {
		result += value;
	});
	return result;
}