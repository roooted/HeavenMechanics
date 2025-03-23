# О программе

![Описание GIF](./demo.gif)

 Программа моделирует движение нескольких небесных тел на основе трех физических законов:
 - Закон всемирного тяготения: $F = G*\frac{m_1*m_2}{r^2}$
 - Второй закон Ньютона: $F = m*a$
 - Кинематический закон движения материальной точки: $x = x_0 + v*t + \frac{a*t^2}{2}$

# Как пользоваться
Сначала необходимо выбрать один из готовых шаблонов, нажав на клавишу "frames". Каждый из шаблонов представляет из себя json файл, содержащий информацию о заданных объектах: масса, начальные координаты и начальная скорость (ее проекции на оси X и Y). Любой из этих параметров можно менять, наблюдая, как это отразится на стабильности системы. Существует два тима объектов - звезды и планеты, которые отличаются друг от друга только отображаемым изображением.
