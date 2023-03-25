# microGPT
The paper analysis and clustering tool powered by chatGPT.
This release is a beta release only and therefore does not provide a flexible workflow.

## Function
This script can help you automatically pull the article directory from IJSEM and get all the content of the specified article chapter.Through the chatGPT api and pre-designed questions (which can be modified at will), you can get answers to specified questions about an article or all species in it.
The output will be placed in a csv file named by current issue that is parsing. You can refer to the file `output_example.csv`.

## Usage
Firstly, You need to have an OpenAi account and generate an API, and replace the value in the openai.api_key at the beginning of the jupyter note with your API.
To run the code, you should have a jupyter notebook environment or just copy all code snippets to a .py file.
The function `establish_dataset()`provides the only one-click generation method.You can modify the capture mode by modifying `mode`, and limit the range of dataset by `volume_range` and `year_limit`, also you can easily modify the require and question by pass parameters to the function. The package requirment are `openai`, `requests` and `bs4`. The Python version I used is 3.10, but using other versions should not cause compatibility issues.
