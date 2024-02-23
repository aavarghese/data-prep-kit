from typing import Any


class ParamsUtils:
    """
    Class implementing support methods for parameters manipulation
    """

    @staticmethod
    def convert_to_ast(d: dict[str, Any]) -> str:
        """
        Converts dictionary to AST string representing the dictionary
        :param d: dictionary
        :return: an AST string
        """
        ast_string = "{"
        first = True
        for key, value in d.items():
            if first:
                first = False
            else:
                ast_string += ", "
            if isinstance(value, str):
                ast_string += f"'{key}': '{value}'"
            else:
                ast_string += f"'{key}': {value}"
        ast_string += "}"
        return ast_string

    @staticmethod
    def dict_to_req(d: dict[str, Any]) -> list[str]:
        """
        Convert dictionary to a list of string parameters
        :param d: dictionary
        :return: an array of parameters
        """
        res = [""]
        for key, value in d.items():
            res.append(f"--{key}={value}")
        return res

    @staticmethod
    def __dict_to_str(help: dict[str, str], initial_indent: str, indent_per_level: str, as_value: bool) -> str:
        all_text = ""
        if as_value:
            all_text = all_text + "{ "
        first = True
        for key, value in help.items():
            if isinstance(value, dict):
                text = ParamsUtils.__dict_to_str(value, initial_indent + indent_per_level, indent_per_level, as_value)
            else:
                if as_value:
                    key = "'" + key + "'"
                    if isinstance(value, str):
                        value = "'" + value + "'"
                text = initial_indent + key + ": " + str(value)
            if first:
                sep = ""
            elif as_value:
                sep = ", "
            else:
                sep = "\n"
            all_text = all_text + sep + text
            first = False
        if as_value:
            all_text = all_text + " }"
        return all_text

    @staticmethod
    def get_ast_help_and_example_text(help_dict: dict[str, str], examples: list[dict[str, Any]]):
        initial_indent = ""
        indent_per_level = "   "
        help_txt = ParamsUtils.__dict_to_str(help_dict, initial_indent, indent_per_level, False)
        if examples is not None:
            example_txt = "\n" + initial_indent
            if len(examples) == 1:
                example_txt += "Example: "
            else:
                example_txt += "Example(s):"
            for example_dict in examples:
                etxt = ParamsUtils.__dict_to_str(example_dict, initial_indent, indent_per_level, True)
                if len(examples) == 1:
                    example_txt = example_txt + etxt
                else:
                    example_txt = example_txt + "\n" + initial_indent + "    " + etxt
        else:
            example_txt = ""
        msg = help_txt + example_txt
        return msg

    @staticmethod
    def get_ast_help_text(help_example_dict: dict[str, list[str, Any]]):
        """
        Create some help text for an AST-formatted parameter value.
        :param help_example_dict:  This dictionary of lists, where they keys
        correspond to the parameter names and the list is a pair of values.
        The value in the list is an example value for the option, the 2nd in is the help text.
        If you need to provide more than 1 example, use get_ast_help_and_example_text() which
        allows a list of examples.
        Example:
            help_example_dict = {
                'access_key': ["AFDSASDFASDFDSF ", 'access key help text'],
                'secret_key': ["XSDFYZZZ", 'secret key help text'],
                'cos_url': ['s3:/cos-optimal-llm-pile/test/', "COS url"]
            }
            parser.add_argument(
                "--s3_cred",
                type=ast.literal_eval,
                default=None,
                help="ast string of options for cos credentials\n" +
                     ParamsUtils.get_ast_help_text(help_example_dict)
            )
        :return:  a string to be included in help text, usually concantentated with the general
        parameter help text.
        """

        help_dict = {}
        example_dict = {}
        for key, value in help_example_dict.items():
            if not isinstance(value, list):
                raise ValueError("key value for key " + key + " is not a list")
            if len(value) != 2:
                raise ValueError("List for key " + key + " is not a list of length 2")
            example_value = value[0]
            help_text = value[1]
            help_dict[key] = help_text
            example_dict[key] = example_value
        return ParamsUtils.get_ast_help_and_example_text(help_dict, [example_dict])
        # return ParamsUtils.get_ast_help_and_example_text(help_dict, [example_dict,example_dict])