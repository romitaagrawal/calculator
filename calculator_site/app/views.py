from django.views import View
from django.shortcuts import render , redirect
import math
from .models import CalculatorHistory
from .serializers import CalculatorHistorySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegisterForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # password is auto-hashed, confirm password auto-validated
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


class HistoryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = CalculatorHistory.objects.filter(user=request.user).order_by('-timestamp')[:10]
        serializer = CalculatorHistorySerializer(history, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CalculatorHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Mathematics:
    def addition(self, a, b): return a + b
    def subtraction(self, a, b): return a - b
    def multiplication(self, a, b): return a * b
    def division(self, a, b): return a / b if b != 0 else float('inf')
    def power(self, a, b): return math.pow(a, b)
    def sin(self, a): return round(math.sin(math.radians(a)), 10)
    def cos(self, a): return round(math.cos(math.radians(a)), 10)
    def tan(self, a): return round(math.tan(math.radians(a)), 10)
    def sinh(self, a): return round(math.sinh(math.radians(a)), 10)
    def cosh(self, a): return round(math.cosh(math.radians(a)), 10)
    def tanh(self, a): return round(math.tanh(math.radians(a)), 10)
    def sqrt(self, a): return math.sqrt(a)
    def log(self, a): return math.log10(a) if a > 0 else float('nan')
    def ln(self, a): return math.log(a) if a > 0 else float('nan')
    def factorial(self, a):
        if a < 0 or not float(a).is_integer():
            raise ValueError("Factorial only defined for non-negative integers.")
        return math.factorial(int(a))
    def modulus(self, a, b):
        return a % b


class Calculator(LoginRequiredMixin, View):
    template_name = 'calculator.html'

    def get(self, request):
        # history = CalculatorHistory.objects.order_by('-timestamp')[:10]
        return render(request, self.template_name,)

    def post(self, request):
        expression = request.POST.get('my_post_param', '')
        expression = self.insert_multiplication(expression)
        result = None
        error_message = ''

        # try:
        result = self.evaluate_expression(expression)
        CalculatorHistory.objects.create(user=request.user, expression=expression, result=result)
        # except Exception as e:
        #     error_message = str(e)

        # history = CalculatorHistory.objects.order_by('-timestamp')[:10]

        return render(request, self.template_name, {
            # 'result': result if not error_message else '',
            'error_message': error_message,
            'get_param': str(result) if result is not None else expression,
            # 'history': history
        })
    def insert_multiplication(self, expr):
        funcs = ["sin", "cos", "tan", "sinh", "cosh", "tanh", "log", "ln", "sqrt", "exp"]
        new_expr = ""
        i = 0
        prev = ''
        while i < len(expr):
            curr = expr[i]
            # Case 1: digit or closing bracket followed by (
            if (prev.isdigit() or prev == ')') and (curr == '(' or any(expr[i:].startswith(f) for f in funcs)):
                new_expr += '*'
            # Case 2: closing bracket followed by digit
            elif prev == ')' and curr.isdigit():
                new_expr += '*'
            new_expr += curr
            prev = curr
            i += 1
        return new_expr

    def evaluate_expression(self, expr):
        if '(' in expr:
            while '(' in expr:
                open_idx = -1
                for i in range(len(expr)):
                    if expr[i] == '(':
                        open_idx = i
                    elif expr[i] == ')' and open_idx != -1:
                        inner_expr = expr[open_idx+1:i]
                        val = self.evaluate_expression(inner_expr)
                        expr = expr[:open_idx] + str(val) + expr[i+1:]
                        break
        expr = self.handle_functions(expr)
        return self.compute_bodmas(expr)

    def handle_functions(self, expr):
        math_obj = Mathematics()
        functions = ["sinh", "cosh", "tanh", "sin", "cos", "tan", "sqrt", "log", "ln"]
        for func in functions:
            while func in expr:
                idx = expr.find(func)
                j = idx + len(func)
                if j < len(expr) and expr[j] == '(':
                    j += 1
                    start = j
                    count = 1
                    while j < len(expr) and count > 0:
                        if expr[j] == '(':
                            count += 1
                        elif expr[j] == ')':
                            count -= 1
                        j += 1
                    value = self.evaluate_expression(expr[start:j-1])
                else:
                    start = j
                    while j < len(expr) and (expr[j].isdigit() or expr[j] == '.' or expr[j] == '-'):
                        j += 1
                    value = float(expr[start:j])
                val = float(value)
                if func == 'sin': res = math_obj.sin(val)
                elif func == 'cos': res = math_obj.cos(val)
                elif func == 'tan': res = math_obj.tan(val)
                elif func == 'sinh': res = math_obj.sinh(val)
                elif func == 'cosh': res = math_obj.cosh(val)
                elif func == 'tanh': res = math_obj.tanh(val)
                elif func == 'sqrt': res = math_obj.sqrt(val)
                elif func == 'log': res = math_obj.log(val)
                elif func == 'ln': res = math_obj.ln(val)
                expr = expr[:idx] + str(res) + expr[j:]
        return expr

    def compute_bodmas(self, expr):
        math_obj = Mathematics()

        expr = expr.replace('e+', 'e').replace('e-', 'ex')

        expr = expr.replace('pi', str(math.pi))

        expr = expr.replace('e', str(math.e))

        # Step 1: Handle factorial (!)
        i = 0
        while i < len(expr):
            if expr[i] == '!':
                # Go left to find the number before '!'
                j = i - 1
                num = ''
                while j >= 0 and (expr[j].isdigit() or expr[j] == '.' or expr[j] == '-'):
                    num = expr[j] + num
                    j -= 1
                if num == '':
                    raise ValueError("No number before factorial (!)")
                val = float(num)
                res = math_obj.factorial(val)
                expr = expr[:j + 1] + str(res) + expr[i + 1:]
                i = j + len(str(res))
            else:
                i += 1

        # Step 2: Handle binary operations (with modulus % added)
        ops = ["^", "*", "/", "%", "+", "-"]
        for op in ops:
            i = 0
            while i < len(expr):
                if expr[i] == op and i != 0:
                    # Extract left operand
                    j = i - 1
                    while j >= 0 and (expr[j].isdigit() or expr[j] == '.' or expr[j] == '-'):
                        j -= 1
                    left = expr[j + 1:i]

                    # Extract right operand
                    k = i + 1
                    while k < len(expr) and (expr[k].isdigit() or expr[k] == '.' or expr[k] == '-'):
                        k += 1
                    right = expr[i + 1:k]

                    if left == '' or right == '':
                        raise ValueError(f"Invalid syntax around operator '{op}'")

                    a = float(left)
                    b = float(right)

                    if op == '^':
                        res = math_obj.power(a, b)
                    elif op == '*':
                        res = math_obj.multiplication(a, b)
                    elif op == '/':
                        res = math_obj.division(a, b)
                    elif op == '%':
                        res = math_obj.modulus(a, b)
                    elif op == '+':
                        res = math_obj.addition(a, b)
                    elif op == '-':
                        res = math_obj.subtraction(a, b)

                    expr = expr[:j + 1] + str(res) + expr[k:]
                    i = -1  # Reset
                i += 1
        expr = expr.replace('ex', 'e-')

        return float(expr)