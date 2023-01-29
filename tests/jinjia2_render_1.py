
import jinja2


if __name__ == '__main__':
    template = jinja2.Template("name: {{name}}")
    kwargs = {
        "name": "lisi"
    }
    r = template.render(**kwargs)
    print(r)

