# Data Processing
## General format:
```
[article]\t[summary]\n
[article]\t[summary]\n
[article]\t[summary]\n
```
Special characters must be handled. See gen-cnn for a general template to create clean text.<br>
Newlines are handled by converting them to `/n` instead of the traditional `\n`<br>
T5 is text-to-text, which means any feature of the text that occurs consitently enough will become present in the final model. Please format the output to require minimal post-processing in production.
## Article formats
See the example (gen-cnn.py).
## Summary formats
This will vary depending on input data, but some ideas:<br>
Bullet points:
```
[article]\t- item1/n- item2/n- item3/n
```
Paragraph:
```
This is the abstract of a research paper....
```