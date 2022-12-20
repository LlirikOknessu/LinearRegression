## Анализ построенной модели
### Линейная регрессия
В данном проекте были созданы несколько линейных моделей: линейной, гребневой регрессий, эластичной сети и лассо. 
Они были использованы для предсказания ожидаемой продолжительности жизни на основе ранее отобранных данных.

Линейная регрессия - Это модель машинного обучения, основанная на предположении, что зависимость в наблюдаемых 
данных можно описать простой прямой.
Гребневая(ридж) регрессия – это регуляризованная версия линейной регрессии. Она заставляет алгоритм обучения не только 
соответствовать данным, но и сохранять веса модели как можно меньшими.
Метод регрессии лассо (LASSO, Least Absolute Shrinkage and Selection Operator) — это вариация линейной регрессии, 
специально адаптированная для данных, которые демонстрируют сильную мультиколлинеарность (то есть сильную корреляцию
признаков друг с другом). Данная модель схожа с гребневой регрессией, однако в ней один из коэффициентов может стать 
нулевым.
Эластичная сеть - это регуляризованный метод регрессии, который объединяет методы лассо и ридж.

Для обучения было создано три этапа: обучение, валидация и выход модели. Для проведения данных этапов было создано три
файла: *linear_regression*, *linear_regression_full*, *linear_regression_validation*. В файле *linear_regression* 
находится этап обучения и тестирования, в *linear_regression_validation* - этап валидации и, наконец, в *linear_regression_full* - этап 
выхода модели. 

Также внутри каждого файла была создана бейзлайн - базовая модель, используемая как ориентир для оценки 
качества работы модели. В нашем случае была использована функция *uniform()*, которая позволила сгенерировать числа в 
диапазоне минимальной и максимальной продолжительности жизни. 

Ниже приведена таблица с результатами работы модели:

| Модель                 | Стадия       | Точность | Среднеквадратичная ошибка модели | Среднеквадратичная ошибка бейзлайна 
|------------------------|--------------|----------|----------------------------------|--------------------------------------
| LinearRegression       | Обучение     | 0.7706   | 3.2312                           | 12.88                                
|                        | Валидация    | 0.7632   | 3.1491                           | 13.14                                
|                        | Выход модели | 0.7896   | 3.091                            | 15.5                                 
| Ridge regression       | Обучение     | 0.7703   | 3.2312                           | 13.07                               
|                        | Валидация    | 0.7629   | 3.1491                           | 13.32                                
|                        | Выход модели | 0.7896   | 3.090                            | 15.8                                 
| Lasso regression       | Обучение     | 0.7508   | 3.3241                           | 13.8                                 
|                        | Валидация    | 0.7314   | 3.2856                           | 13.05                                
|                        | Выход модели | 0.7669   | 3.1771                           | 15.43                                
| Elastic net regression | Обучение     | 0.7514   | 3.3259                           | 12.81                                
|                        | Валидация    | 0.7319   | 3.2739                           | 13.2                                 
|                        | Выход модели | 0.7681   | 3.1702                           | 15.59     

После проведения обучения видно, что в целом, для любой модели регрессии, точность составляет более 70 процентов и 
среднеквадратичная ошибка значительно меньше базовой модели.

Самыми лучшими вариантами являются модели линейной регрессии, так как точность у данных регрессий выше всего, а 
среднеквадратичная ошибка ниже. Конечно, у модели линейной регрессии точность в целом немного выше, однако крайне 
незначительно. После идет модель эластичной сети, а только потом - лассо. 

Можно предположить, что такие результаты были получены вследствие того, что данные в основном выбирались с линейной 
зависимостью, поэтому линейная регрессия и ридж имеют самую высокую точность. Кроме того, гребневая регрессия лучше 
подходит в ситуации, когда мы хотим сделать приоритетными большое количество переменных, каждая из которых имеет 
небольшой эффект, что и было представлено в наших данных. Лассо же показало результат похуже, так как ее используют в 
основном тогда, когда в модели требуется учитывать несколько переменных, каждая из которых имеет средний или большой 
эффект.

### Деревья решений 
(Краткий вывод, полный с графиками и табличками в отчете)

В целом по моделям деревьев решений можно сказать, что они лучше справились 
с задачей предсказания продолжительности жизни, чем модели линейной регрессии,
так как их точность больше 90%, а среднеквадратичная ошибка в несколько раз ниже.
Также выявлено, что модели случайного леса и экстра-деревьев справляются незначительно 
лучше обычной модели дерева решений, что в целом достаточно ожидаемо. Кроме того, можно 
предположить, что модель случайного леса справляется несколько лучше, чем модель экстра-деревьев,
так как в ней выбирается оптимальный параметр разделения. 