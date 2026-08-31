
<h1 align="center">An Analysis of the Musical Affordances of No-Data Training</h1>
<h2 align="center">Supplementary material</h2>
<p align="center"><a href="https://github.com/oflaig/no-data-affordances">Thesis</a> - <a href="https://github.com/oflaig/no-data-affordances">Code</a></p>

## Abstract
This thesis presents a method for training neural synthesisers in a closed, feedback-like system, allowing for real-time output of the generated audio and real-time interference in the training regime. A simple interface facilitates the exploration of the training itself as musical material, in the manner of similar work with dynamical systems. This interface is provided to three users, and they are interviewed about their experience.

The affordance framework, an analytical tool for understanding users' interactions with an `artifact', is then used to link each user's feedback with relevant details of their own musical and technical practice, as well as to the design of the system. By comparing and contrasting each user's experiences, an understanding of the underlying affordances of no-data training is developed. 

Through this analysis, no-data training is found to encourage the musical exploration of machine learning training dynamics, particularly those that produce gradually and continuously evolving sounds; it is also found to discourage the deterministic control of sonic features and the close control of the system as a whole. The results of this analysis are situated within its limitations and conscious subjective biases. Directions for further study are suggested, including technical developments on the proposed system, but also focussing on approaches for understanding no-data training in a wider variety of musical contexts through `instrumentalisation'.

## Sound examples

<table>
  <tr>
    <th style="vertical-align:top;width:5%">Version</th>
    <th style="vertical-align:top;width:40%">Description</th>
    <th style="text-align:center;width:55%">Demonstration</th>    
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
  <tr>
    <td>1</td>
    <td>In this first version, visual models were also available. Here, an MLP is used on the right, and a harmonic generator with 20 harmonics on the left. A shorter <em>Time factor</em> is used here, increasing the perceived rate of training as the audio produced per frame is shorter. The <em>Frequency skew</em> parameter is used to influence the pitch at around 15 seconds.</td>
    <td>
        <video width="320" height="240" controls>
            <source src="demos/v1/time1_frames20_mlpgen.mp4" type="video/mp4">
        </video>
    </td>
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
  <tr>
    <td>2</td>
    <td>This demonstration shows the more stable dynamics of the second version of the instrument, with the pitch of the generators guided with the <em>Frequency skew</em> parameter.
    <td>
        <video width="320" height="240" controls>
            <source src="demos/v2/demo.mp4" type="video/mp4">
        </video>
    </td>
  </tr>
  <tr>
    <td>2</td>
    <td>A demonstration of version two's <em>Regularisation</em> parameter. This control is varied for the generator on the right, and the learned parameters can be heard to gradually become smoother, with the f0 curve flattening, and less variation between the gains of the harmonics.
    <td>
        <video width="320" height="240" controls>
            <source src="demos/v2/regularisation.mp4" type="video/mp4">
        </video>
    </td>
  </tr>
    <tr>
    <td>3</td>
    <td>A demonstration of the <em>Quantisation</em> parameter introduced in version 3. Its effect is especially noticeable when the <em>Tuning</em> parameter is changed, but loses its effect when the other optimiser is introduced. Also heard is the step-like interpolation, used to highlight the effect of the quantisation.
    <td>
        <video width="320" height="240" controls>
            <source src="demos/v3/quantisation.mp4" type="video/mp4">
        </video>
    </td>
  </tr>
</table>


