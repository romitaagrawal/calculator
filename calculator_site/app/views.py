from django.views import View
from django.shortcuts import render
import math
from ipdb import set_trace

# Simple math class
class Mathematics:
    def addition(self,a, b):
        return a + b

    def subtraction(self,a, b):
        return a - b

    def multiplication(self,a, b):
        return a * b

    def division(self,a, b):
        if b == 0:
            return ("division by zero")
        return a / b

    def sin(self,a):
        return math.sin(math.radians(a))
    
    def cos(self,a): 
        return math.cos(math.radians(a))
    
    def tan(self,a): 
        return math.tan(math.radians(a))
    
    def sinh(self,a):
        return math.sinh(a)

    def cosh(self,a):
        return math.cosh(a)

    def tanh(self,a):
        return math.tanh(a)
    
    def log(self, a): 
        return math.log10(a)     
    
    def ln(self, a): 
        return math.log(a)      
    
    def sqrt(self, a): 
        return math.sqrt(a)
    
    def power(self, a, b): 
        return math.pow(a, b)
    


class Calculator(View):
    template_name = 'calculator.html'
    
    def get(self, req, *args, **kwargs):
        # Render calculator with blank state
        return render(req, self.template_name)

    def post(self, request, *args, **kwargs):
        expression = request.POST.get('my_post_param', '')
        expression = self.insert_multiplication(expression)
        answer = None
        error_message = ""

        try:
            answer = self.bodmas(expression)
            expression = str(answer)
            # while type(expression) != float:
            #     o, a, b, part = self.bodmas(expression)
            #     answer = self.evaluation(o, a, b)
            #     expression = expression.replace(part, str(answer))

            #     try:
            #         expression = float(expression)
            #     except:
            #         pass

        except Exception as e:
            error_message = str(e)

        context = {
            'get_param': str(answer) if answer is not None else expression,
            'result': expression if not error_message else '',
            'error_message': error_message
        }

        return render(request, self.template_name, context)

    
    def insert_multiplication(self, expression):
        new_expr = ""
        prev = ""
        funcs = ["sin", "cos", "tan","sinh", "cosh", "tanh", "log", "ln", "sqrt"]  # "sinh", "cosh", "tanh",
        i = 0

        while i < len(expression):
            curr = expression[i]

            # Case 1: number or ')' followed by '('
            if (prev.isdigit() or prev == ')') and curr == '(':
                new_expr += '*'

            # Case 2: ')' followed by number
            elif prev == ')' and curr.isdigit():
                new_expr += '*'

            # Case 3: digit or ')' followed by a function name (e.g., 2sin → 2*sin)
            elif (prev.isdigit() or prev == ')') and any(expression[i:].startswith(func) for func in funcs):
                new_expr += '*'

            new_expr += curr
            prev = curr
            i += 1

        return new_expr

    
    
    def evaluation(self, o, a, b):
        answer = 0
        m = Mathematics()
        if o == "+":
            answer = m.addition(a,b)
        if o == "-":
            answer = m.subtraction(a,b)
        if o == "*":
            answer = m.multiplication(a,b)
        if o == "/":
            answer = m.division(a,b)
        if o == "^":
            answer = m.power(a,b)
        if o == "sin":
            answer = m.sin(a)
        if o == "cos":
            answer = m.cos(a)
        if o == "tan":
            answer = m.tan(a)
        if o == "sinh":
            answer = m.sinh(a)
        if o == "cosh":
            answer = m.cosh(a)
        if o == "tanh":
            answer = m.tanh(a)
        if o == "log": 
            answer= m.log(a)
        if o == "ln": 
            answer= m.ln(a)
        if o == "sqrt":
            answer= m.sqrt(a)
        
        return answer
        
        
    def bodmas(self, expression):
        funcs = ["sinh", "cos", "tan", "sin", "cosh", "tanh", "log", "ln", "sqrt"]
        
        while '(' in expression:
            open_idx = -1
            for i, char in enumerate(expression):
                if char == '(':
                    open_idx = i
                elif char == ')' and open_idx != -1:
                    sub_expr = expression[open_idx + 1:i]
                    value = self.bodmas(sub_expr)  # Recursively solve inner expr
                    expression = expression[:open_idx] + str(value) + expression[i + 1:]
                    break

        # Handle functions: sin, cos, etc.
        for func in funcs:
            while func in expression:
                i = expression.find(func)
                j = i + len(func)
                num = ""
                while j < len(expression) and (expression[j].isdigit() or expression[j] == '.' or expression[j] == '-'):
                    num += expression[j]
                    j += 1
                if num == "":
                    raise ValueError(f"Missing number after function '{func}'")
                result = self.evaluation(func, float(num), 0)
                expression = expression[:i] + str(result) + expression[j:]

        # Handle implicit multiplication: e.g., 2sin(30) or 3(4+5)
        i = 0
        while i < len(expression) - 1:
            if (expression[i].isdigit() or expression[i] == ')') and (expression[i + 1].isalpha() or expression[i + 1] == '('):
                expression = expression[:i + 1] + '*' + expression[i + 1:]
            i += 1

        # Now, process operators in order of precedence
        ops = ["^", "*", "/", "+", "-"]
        for op in ops:
            i = 0
            while i < len(expression):
                if expression[i] == op:
                    # Extract left number
                    j = i - 1
                    left = ""
                    while j >= 0 and (expression[j].isdigit() or expression[j] == '.' or expression[j] == '-'):
                        left = expression[j] + left
                        j -= 1

                    # Extract right number
                    k = i + 1
                    right = ""
                    while k < len(expression) and (expression[k].isdigit() or expression[k] == '.' or expression[k] == '-'):
                        right += expression[k]
                        k += 1

                    if left == "" or right == "":
                        raise ValueError(f"Syntax error around operator '{op}'")

                    a = float(left)
                    b = float(right)
                    result = self.evaluation(op, a, b)

                    expression = expression[:j + 1] + str(result) + expression[k:]
                    i = -1  # Restart
                i += 1

        return float(expression)
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # def bodmas(self, expression):
    #     funcs = ["sinh", "cos", "tan","sin", "cosh", "tanh", "log", "ln", "sqrt"]  # "sinh", "cosh", "tanh"
    #     for func in funcs:
    #         # set_trace()
    #         if expression.split('(')[0] == func:
                
    #             i = expression.find(func)
    #             start = i + len(func) + 1
    #             end = expression.find(")", start)
    #             if end == -1:
    #                 raise ValueError(f"Missing closing parenthesis in {func}")
    #             val = expression[start:end]
    #             num = float(eval(val))  # Allow expression inside sin(45+45)
    #             part = expression[i:end + 1]
    #             return func, num, 0, part

    #     for op in ["^", "/", "*", "+", "-"]:
    #         i = self.find_operator_outside_parentheses(expression, op)
    #         if i != -1:
    #             a, b, part = self.get_numbers(expression, i)
    #             return op, a, b, part

    #     return "", 0, 0, expression

    # def find_operator_outside_parentheses(self, expr, operator):
    #     depth = 0
    #     for i in range(len(expr)):
    #         if expr[i] == '(':
    #             depth += 1
    #         elif expr[i] == ')':
    #             depth -= 1
    #         elif expr[i] == operator and depth == 0:
    #             return i
    #     return -1

    # def get_numbers(self, expr, idx):
    #     # LEFT
    #     j = idx - 1
    #     if expr[j] == ')':
    #         count = 1
    #         j -= 1
    #         while j >= 0 and count > 0:
    #             if expr[j] == ')':
    #                 count += 1
    #             elif expr[j] == '(':
    #                 count -= 1
    #             j -= 1
    #         left = expr[j + 1:idx]
    #     else:
    #         left = ""
    #         while j >= 0 and (expr[j].isdigit() or expr[j] == '.' or expr[j] == '-'):
    #             left = expr[j] + left
    #             j -= 1

    #     # RIGHT
    #     k = idx + 1
    #     if expr[k] == '(':
    #         count = 1
    #         k += 1
    #         start = k
    #         while k < len(expr) and count > 0:
    #             if expr[k] == '(':
    #                 count += 1
    #             elif expr[k] == ')':
    #                 count -= 1
    #             k += 1
    #         right = expr[idx + 1:k]
    #     else:
    #         right = ""
    #         while k < len(expr) and (expr[k].isdigit() or expr[k] == '.' or expr[k] == '-'):
    #             right += expr[k]
    #             k += 1

    #     if not left.strip() or not right.strip():
    #         raise ValueError(f"Syntax error near '{expr[idx]}': missing operand.")

    #     try:
    #         a = float(eval(left))
    #         b = float(eval(right))
    #     except:
    #         raise ValueError(f"Invalid expressions near '{expr[idx]}': '{left}' and '{right}'")

    #     part = expr[j + 1:k]
    #     return a, b, part
    
    