<?php
abstract class Animal{
protected $nombre;


function__construct($nombre)
{
    $this->nombre = $nombre;
}

abstract function HacerSonido();}


class Perro extends Animal{
    public function HacerSonido():{}
        echo " $this->nombre Guau";
    }
    public function Jugar():{
        echo "$this->nombre El perro esta jugando";
    }

class Gato extends Animal{
    public function HacerSonido:(){
    echo "$this->nombre Miau";
}
}
public function dormir(){
    echo "$this->nombre El gato esta durmiendo";}


$perro = new Perro("perro");
$Gato = new Gato("gato"):

$perro -> HacerSonido();
$perro -> Jugar();

$gato -> HacerSonido();
$gato -> dormir();

?>