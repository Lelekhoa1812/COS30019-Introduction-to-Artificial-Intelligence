function go() {
	var input = document.getElementById("expressionInput").value;
	try {		
		prettyPrintTruthTable(parse(input));
	} catch (e) {		  
		if (e.description !== undefined) {
			displayCompileError(input, e);
		} else {
			throw e;
		}
	}
}
function assert(expr, what) {
	if (expr === false) {
		throw new Error("Assertion failed: " + what);
	}
}
function unreachable(why) {
	throw new Error("Unreachable code: " + why);
}