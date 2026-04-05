echo off
echo Хотели бы вы начать установку frontend(-а) с самого нуля?(y/n)
set /p input="y/n"
IF input ( npm i )
npm run dev