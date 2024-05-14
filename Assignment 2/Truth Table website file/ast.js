function trueNode() {}

trueNode.prototype.evaluate = function(assignment) {
	return true;
}
trueNode.prototype.toString = function(variables) {
	return "&#8868;";
}

/*** Node type for F. ***/
function falseNode() {}
falseNode.prototype.evaluate = function(assignment) {
	return false;
}
falseNode.prototype.toString = function(variables) {
	return "&#8869;";
}

/*** Node type for ~. ***/
function negateNode(underlying) {
	this.underlying = underlying;
}
/* To evaluate ~, we evaluate the underlying expression and negate the result. */
negateNode.prototype.evaluate = function(assignment) {
	return !this.underlying.evaluate(assignment);
}
negateNode.prototype.toString = function(variables) {
	return "&not;" + this.underlying.toString(variables);
}

/*** Node type for /\ ***/
function andNode(lhs, rhs) {
	this.lhs = lhs;
	this.rhs = rhs;
}
andNode.prototype.evaluate = function(assignment) {
	return this.lhs.evaluate(assignment) && this.rhs.evaluate(assignment);
}
andNode.prototype.toString = function(variables) {
	return "(" + this.lhs.toString(variables) + " &and; " + this.rhs.toString(variables) + ")";
}

/*** Node type for \/ ***/
function orNode(lhs, rhs) {
	this.lhs = lhs;
	this.rhs = rhs;
}

orNode.prototype.evaluate = function(assignment) {
	return this.lhs.evaluate(assignment) || this.rhs.evaluate(assignment);
}
orNode.prototype.toString = function(variables) {
	return "(" + this.lhs.toString(variables) + " &or; " + this.rhs.toString(variables) + ")";
}

/*** Node type for -> ***/
function impliesNode(lhs, rhs) {
	this.lhs = lhs;
	this.rhs = rhs;
}

/* Use the equivalcen p -> q   ===   ~p \/ q */
impliesNode.prototype.evaluate = function(assignment) {
	return !this.lhs.evaluate(assignment) || this.rhs.evaluate(assignment);
}
impliesNode.prototype.toString = function(variables) {
	return "(" + this.lhs.toString(variables) + " &rarr; " + this.rhs.toString(variables) + ")";
}

/*** Node type for <-> ***/
function iffNode(lhs, rhs) {
	this.lhs = lhs;
	this.rhs = rhs;
}
iffNode.prototype.evaluate = function(assignment) {
	return this.lhs.evaluate(assignment) === this.rhs.evaluate(assignment);
}
iffNode.prototype.toString = function(variables) {
	return "(" + this.lhs.toString(variables) + " &harr; " + this.rhs.toString(variables) + ")";
}

/*** Node type for variables ***/
function variableNode(index) {
	this.index = index;
}

/* The value of a variable is given by taking the value given to that variable in the explicit assignment. */
variableNode.prototype.evaluate = function(assignment) {
	return assignment[this.index];
}
variableNode.prototype.toString = function(variables) {
	return variables[this.index];
}