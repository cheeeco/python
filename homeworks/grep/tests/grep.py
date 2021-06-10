import re
import argparse
import sys


def output(line):
    print(line)

def grep(lines, params):
    last_printed = -1
    before = max(params.before_context, params.context)
    after = max(params.after_context, params.context)
    
#ignore_case arg    
    if params.ignore_case:
        regex_pattern = re.compile(params.pattern, re.IGNORECASE)
    else:
        regex_pattern = re.compile(params.pattern)
    
    output('\n')
    
#invert search arg
    for i, line in enumerate(lines):
        line = line.rstrip()

        regex_match = regex_pattern.search(line)
        
        if bool(regex_match) != bool(params.invert):
#before_context
            if before:
                for j in range(max(last_printed + 1, i - before), i):
                    if params.line_number:
                        output("%d: %s" % (j, lines[j].rstrip()))
                    else:
                        output(lines[j].rstrip())
                        
                    last_printed = i - 1
                
#выводим мэтч, если ещё не вывели
            if i > last_printed:
                if params.line_number:
                    output("%d: %s" % (i, line))
                else:
                    output(line)
                
                last_printed = i
            
#after_context
            if after:
                for j in range(max(last_printed + 1, i + 1), min(i + after + 1, len(lines))):
                    if params.line_number:
                        output("%d: %s" % (j, lines[j].rstrip()))
                    else:
                        output(lines[j].rstrip())
                        
                    last_printed = min(i + after + 1, len(lines)) - 1


def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)

if __name__ == '__main__':
    main()
