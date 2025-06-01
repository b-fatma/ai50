import sys

from crossword import *

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            # A copy is used to avoid `RuntimeError: Set changed size during iteration` 
            for x in self.domains[var].copy():
                if len(x) != var.length:
                    self.domains[var].remove(x) 

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        for x_value in self.domains[x].copy():
            if self.crossword.overlaps[x, y] is not None:
                i, j = self.crossword.overlaps[x, y]
                if all([x_value[i] != y_value[j] for y_value in self.domains[y]]):
                    self.domains[x].remove(x_value)
                    revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """ 
        if arcs is None:
            arcs = [key for key in self.crossword.overlaps.keys() if self.crossword.overlaps[*key] is not None]

        while len(arcs) > 0:
            x, y = arcs.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        arcs.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return all([var in assignment.keys() and assignment[var] is not None for var in self.crossword.variables])

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # all values are distinct ?
        if len(assignment.values()) != len(set(assignment.values())):
            return False
        # every value is the correct length ?
        if not all([len(assignment[var]) == var.length for var in assignment.keys()]):
            return False
        # there are no conflicts between neighboring variables ?
        for x in assignment.keys():
            for n in self.crossword.neighbors(x):
                if n in assignment.keys():
                    i, j = self.crossword.overlaps[x, n]
                    if assignment[x][i] != assignment[n][j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        def compute_constraining_values(self, var, value, assignment):
            n = 0
            for unassigned_neighbor in [item for item in self.crossword.neighbors(var) if item not in assignment.keys()]:
                if self.crossword.overlaps[var, unassigned_neighbor]:
                    i, j = self.crossword.overlaps[var, unassigned_neighbor]
                    for unassigned_neighbor_value in self.domains[unassigned_neighbor]:
                        if value[i] != unassigned_neighbor_value[j]:
                            n += 1
            return n
        
        values = [value for value in self.domains[var]]
        constraining_values = {value: compute_constraining_values(self, var, value, assignment) 
                               for value in self.domains[var]}
        
        return sorted(values, key=constraining_values.__getitem__)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        def compute_remaining_values(self, unassigned_variables):
            remaining_values= {}
            for var in unassigned_variables:
                remaining_values[var] = len(self.domains[var])
            return remaining_values
        
        def compute_degrees(self, unassigned_variables):
            degrees = {}
            for var in unassigned_variables:
                degrees[var] = len(self.crossword.neighbors(var))
            return degrees
        
        unassigned_variables = [item for item in self.crossword.variables if item not in assignment.keys()]
        remaining_values = compute_remaining_values(self, unassigned_variables)
        min_remaining_values = [var for var in remaining_values.keys() if remaining_values[var] == min(remaining_values.values())]

        if len(min_remaining_values) == 1:
            return min_remaining_values[0]
        
        degrees = compute_degrees(self, min_remaining_values)
        highest_degrees = [var for var in degrees.keys() if degrees[var] == min(degrees.values())]
        return highest_degrees[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            temp_assignment = assignment.copy()
            temp_assignment[var] = value
            if self.consistent(temp_assignment):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                assignment.pop(var)
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
