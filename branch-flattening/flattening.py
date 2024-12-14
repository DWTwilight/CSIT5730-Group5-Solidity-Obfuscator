import re
import random
import argparse
from utils import gen_distinct_labels, gen_random_identifier


class FlatteningContext:
    def __init__(self, path: str):
        # File must be Solidity source code (*.sol)
        assert path.endswith(".sol"), "File must be Solidity source code (*.sol)"

        # Read file
        with open(path, "r") as f:
            self.src = f.read()

        # save the line with SPDX-License-Identifier
        self.license = re.search(r"// SPDX-License-Identifier:.*", self.src)
        self.license = self.license.group(0) if self.license else ""

        # remove all kinds of comments in Solidity
        self.src = re.sub(r"//.*", "", self.src)
        self.src = re.sub(r"/\*[\s\S]*?\*/", "", self.src)

    def __find_paired_right_brace(self, start: int) -> int:
        # find the index of the paired right brace of the given left brace
        assert (
            self.src[start] == "{"
        ), "The given index must be the index of a left brace"

        # count of left braces
        count = 1
        # current index
        i = start + 1

        # scan until we find the paired right brace
        while i < len(self.src):
            if self.src[i] == "{":
                count += 1
            elif self.src[i] == "}":
                count -= 1
                if count == 0:
                    return i
            i += 1

        raise ValueError("No paired right brace found")

    def __replace_break_continue(
        self, body: str, state_identifier: str, stop_label: str, next_label: str
    ) -> str:
        # TODO: break/continue statements in a nested loop should not be changed
        # replace continue statements
        body = re.sub(
            r"continue\s*;", f"{state_identifier} = {next_label}; continue;", body
        )
        # replace break statements
        body = re.sub(
            r"break\s*;", f"{state_identifier} = {stop_label}; continue;", body
        )
        return body

    def flatten_while(self) -> str:
        """
        Flatten all non-nested while loops in the source code.
        """
        # find all while loops
        while_iter = re.finditer(r"while\s*\((.*?)\)\s*\{", self.src)
        snippets = []

        lastend = 0

        for loop in while_iter:
            # replace while loop with flattened ones
            if loop.start() >= lastend:  # if the loop is not nested
                if loop.start() > lastend:
                    snippets.append(self.src[lastend : loop.start()])
                lastend = self.__find_paired_right_brace(loop.end() - 1) + 1
                snippets.append(self.__flatten_while(loop, lastend))

        snippets.append(self.src[lastend:])
        return "".join(snippets)

    def __flatten_while(self, loop: re.Match, end: int) -> str:
        # flatten the matched while loop
        condition = loop.group(1)
        body = self.src[loop.end() : end - 1]

        COND_LABEL, BODY_LABEL, STOP_LABEL = gen_distinct_labels(3)
        state_identifier = gen_random_identifier()

        body = self.__replace_break_continue(
            body, state_identifier, STOP_LABEL, COND_LABEL
        )

        result = "\n".join(
            [
                "{",
                f"    uint256 {state_identifier} = {COND_LABEL};",
                "    while (true) {",
                f"        if ({state_identifier} == {COND_LABEL}) {{ {state_identifier} = ({condition}) ? {BODY_LABEL} : {STOP_LABEL}; }}",
                f"        else if ({state_identifier} == {BODY_LABEL}) {{{body} {state_identifier} = {COND_LABEL}; }}",
                f"        else if ({state_identifier} == {STOP_LABEL}) {{break; }}",
                "}}",
            ]
        )

        return result

    def flatten_do_while(self) -> str:
        """
        Flatten all non-nested do-while loops in the source code.
        """
        do_while_iter = re.finditer(
            r"do\s*\{(.*?)\}\s*?while\s*?\((.*?)\)\s*?;", self.src, flags=re.DOTALL
        )
        snippets = []

        lastend = 0

        for loop in do_while_iter:
            if loop.start() >= lastend:
                if loop.start() > lastend:
                    snippets.append(self.src[lastend : loop.start()])
                snippets.append(self.__flatten_do_while(loop))
                lastend = loop.end()

        snippets.append(self.src[lastend:])
        return "".join(snippets)

    def __flatten_do_while(self, loop: re.Match) -> str:
        # flatten the matched do-while loop
        condition = loop.group(2)
        body = loop.group(1)

        COND_LABEL, BODY_LABEL, STOP_LABEL = gen_distinct_labels(3)
        state_identifier = gen_random_identifier()

        body = self.__replace_break_continue(
            body, state_identifier, STOP_LABEL, COND_LABEL
        )

        result = "\n".join(
            [
                "{",
                f"    uint256 {state_identifier} = {BODY_LABEL};",
                "    while (true) {",
                f"        if ({state_identifier} == {COND_LABEL}) {{ {state_identifier} = ({condition}) ? {BODY_LABEL} : {STOP_LABEL}; }}",
                f"        else if ({state_identifier} == {BODY_LABEL}) {{{body} {state_identifier} = {COND_LABEL}; }}",
                f"        else if ({state_identifier} == {STOP_LABEL}) {{break; }}",
                "}}",
            ]
        )

        return result

    def flatten_for(self) -> str:
        """
        Flatten all non-nested for loops in the source code.
        """
        # find all for loops
        for_iter = re.finditer(r"for\s*\((.*);(.*);(.*)\)\s*\{", self.src)
        snippets = []

        lastend = 0

        for loop in for_iter:
            # replace while loop with flattened ones
            if loop.start() >= lastend:  # if the loop is not nested
                if loop.start() > lastend:
                    snippets.append(self.src[lastend : loop.start()])
                lastend = self.__find_paired_right_brace(loop.end() - 1) + 1
                snippets.append(self.__flatten_for(loop, lastend))

        snippets.append(self.src[lastend:])
        return "".join(snippets)

    def __flatten_for(self, loop: re.Match, end: int) -> str:
        # flatten the matched for loop
        pre, condition, post = loop.group(1), loop.group(2), loop.group(3)
        pre = pre + ";"
        post = post + ";"
        body = self.src[loop.end() : end - 1]

        COND_LABEL, BODY_LABEL, STOP_LABEL, POST_LABEL = gen_distinct_labels(4)
        state_identifier = gen_random_identifier()

        body = self.__replace_break_continue(
            body, state_identifier, STOP_LABEL, POST_LABEL
        )

        result = "\n".join(
            [
                "{",
                f"    {pre}",
                f"    uint256 {state_identifier} = {COND_LABEL};",
                "    while (true) {",
                f"        if ({state_identifier} == {COND_LABEL}) {{ {state_identifier} = ({condition}) ? {BODY_LABEL} : {STOP_LABEL}; }}",
                f"        else if ({state_identifier} == {BODY_LABEL}) {{{body} {state_identifier} = {POST_LABEL}; }}",
                f"        else if ({state_identifier} == {STOP_LABEL}) {{break; }}",
                f"        else if ({state_identifier} == {POST_LABEL}) {{ {post} {state_identifier} = {COND_LABEL}; }}",
                "}}",
            ]
        )

        return result

    def flatten(self) -> str:
        self.src = self.flatten_while()
        self.src = self.flatten_do_while()
        self.src = self.flatten_for()
        return self.license + "\n" + self.src
    

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("sol_file")
    args.add_argument("-o", "--output", required=True)
    args = args.parse_args()

    ctx = FlatteningContext(args.sol_file)
    # create path if not exists
    import os
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, "w") as f:
        f.write(ctx.flatten())
