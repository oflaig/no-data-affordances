
<h1 align="center">An Analysis of the Musical Affordances of No-Data Training</h1>
<h2 align="center">Supplementary material</h2>
<p align="center"><a href="https://github.com/oflaig/no-data-affordances">Thesis</a> - <a href="https://github.com/oflaig/no-data-affordances">Code</a></p>

## Abstract

## Sound examples

<table>
  <tr>
    <th style="vertical-align:top;width:5%">Version</th>
    <th style="vertical-align:top;width:40%">Description</th>
    <th style=""text-align:center;width:55%">Demonstration</th>    
  </tr>
  <tr>
    <td>1</td>
    <td>A demonstration of the first version of the system. The output spectrograms of each generator are shown in the top left and right, with the audio heard in the corresponding stereo channel. The use of the learning rate to bring together the output of the two generators is shown. At the end, the "death" described on page 21 is seen, in which the outputs of the two generators becomes stuck at an extreme of their f0 parameter, and parameter changes no longer have an effect.</td>
    <td>
        <video width="320" height="240" controls>
            <source src="demos/v1/demo.mp4" type="video/mp4">
        </video>
    </td>
  </tr>
    <tr>
    <td>1</td>
    <td>This demonstration shows the death described on page 18, in which the volume of the generators is lost - the changing of the parameters then has no effect.</td>
    <td>
        <video width="320" height="240" controls>
            <source src="demos/v1/death.mp4" type="video/mp4">
        </video>
    </td>
  </tr>
    </tr>
    <tr>
    <td>1</td>
    <td>In this first version, visual models were also available. Here, an MLP is used on the right, and a harmonic generator with 20 harmonics on the left. A shorter <em>Time factor</em> is used here, increasing the perceived rate of training as the audio produced per frame is shorter. The <em>Frequency skew</em> parameter is used to influence the pitch at around 15 seconds.</td>
    <td>
        <video width="320" height="240" controls>
            <source src="demos/v1/time1_frames20_mlpgen.mp4" type="video/mp4">
        </video>
    </td>
  </tr>
    </tr>
    <tr>
    <td>1</td>
    <td>This shows the use of a larger <em>Time factor</em>, here set to 16. The first user highlighted how larger values changed the development of the sound from a shifting timbre to "variations on a theme," due to its clearer melodic content. Due to the increased gap between training steps, this can make the system feel less responsive, as changes take longer to take effect.</td>
    <td>
        <video width="320" height="240" controls>
            <source src="demos/v1/20frames16time_death.mp4" type="video/mp4">
        </video>
    </td>
  </tr>
</table>


