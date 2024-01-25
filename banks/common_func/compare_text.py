import difflib as dl


def compare_strings(old_str: str, new_str: str, filename_html: str) -> None:
    show_pre = old_str.replace('\n\n', '\n').splitlines()
    show_aft = new_str.replace('\n\n', '\n').splitlines()

    difference = dl.HtmlDiff().make_file(fromlines=show_pre, tolines=show_aft, charset='utf-8')

    difference_report = open(filename_html, 'w+', encoding='utf-8')
    difference_report.write(difference)
    difference_report.close()


