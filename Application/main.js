import {UndirectedGraph} from 'graphology';
import WebGLRenderer from 'sigma/renderers/webgl';
import { get } from 'https';
import $ from 'jquery';
import { parse } from 'url';
import { type, cpus } from 'os';




let baricenter_promise_3D = fetch('/barycenter_coordinates_3D.json')
  .then(function(response) {
    return response.json();
  })

let media_promise_3D = fetch('/reg_dim_mean_features_media_data_3D.json')
  .then(function(response) {
    return response.json();
  })

let stories_promise_3D = fetch('/reg_dim_mean_features_stories_transform_3D.json')
  .then(function(response) {
    return response.json();
  })


let baricenter_promise_2D = fetch('/barycenter_coordinates_2D.json')
  .then(function(response) {
    return response.json();
  })

let media_promise_2D = fetch('/reg_dim_mean_features_media_data_2D.json')
  .then(function(response) {
    return response.json();
  })

let stories_promise_2D = fetch('/reg_dim_mean_features_stories_transform_2D.json')
  .then(function(response) {
   return response.json();
  })

const highlight_color = '#FF0000';
const transparent_color = '#c8c3c5';
const baricenter_color = '#ff0080';


let media_wanted_id = 0;
let specific_state = false;
let validite = true;


let X = document.getElementsByName("X");
for (let i = 0; i < X.length; i++) {
    X[i].addEventListener("change", function (x) {
      let y_value = document.querySelector('input[name="Y"]:checked').value;
      let error = document.getElementById("sameDimError");
      if (y_value == x.target.value){
        error.textContent = "Vous avez selectionner deux fois la même dimension";
        validite = false;

      }
      else {
        error.textContent = "  ";
        validite = true;
      }
    });
}

let Y = document.getElementsByName("Y");
for (let i = 0; i < Y.length; i++) {
    Y[i].addEventListener("change", function (y) {
      let x_value = document.querySelector('input[name="X"]:checked').value;
      let error = document.getElementById("sameDimError");
      if (x_value == y.target.value){
        error.textContent = "Vous avez selectionner deux fois la même dimension";
        validite = false;
      }
      else {
        error.textContent = "  ";
        validite = true;
      }
    });
}


function set_colors(media_data) {
  let colors = {};
  for ( let i = 0; i < media_data.length; i++ ) {
    let media = media_data[i];
    let color = '';
    do {
      color = '#'+(Math.random()*0xFFFFFF<<0).toString(16);
      } while (Object.values(colors).includes(color) || color == '#FF0000');
    colors[media['id']] = color;
  }

  return colors;
}

function set_sources(stories_data) {
  let sources = {};
  for ( let i = 0; i < stories_data.length; i++) {
    let story = stories_data[i];
    sources[story['story_id']] = story['media_id'];
  }
  return sources;
}




const baricenters_id = ['un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit'];

function get_node_type(node) {
  if (baricenters_id.includes(node)) {
    return "baricenter";
  }
  else if (node.length > 6) {
    return "story";
  }
  else {
    return "media";
  }
}

function get_position(node) {
  let position = "";
  switch (node) {
    case 'un':
      position = "Positif sur les dimensions 1, 2 et 3."
      break;
    case 'deux':
      position = "Positif sur les dimensions 1 et 2, négatif sur la 3."
      break;
    case 'trois':
      position = "Positif sur la dimension 1, négatif sur les dimension 2 et 3."
      break;
    case 'quatre':
      position = "Négatif sur les dimensions 1, 2 et 3."
      break;
    case 'cinq':
      position = "Positif sur les dimension 2 et 3, négatif sur la 1."
      break;
    case 'six':
      position = "Positif sur la dimensions 2, négatif sur 1 et 3.";
      break;
    case 'sept':
      position = "Positif sur les dimensions 1 et 3, négatif sur la 2."
      break;
    case 'huit':
      position = "Positif sur la dimension 3, négatif sur les 1 et 2."
      break;
  }
  return position;
}

function get_media_quarter(media_wanted_id, z) {
  for (let i = 0; i < media_data.length; i++){
    var media = media_data[i];
    if (media['id'] === media_wanted_id) { break;}
  }
  if (media[z] >= 0) { return "positif";}
  else { return "negatif";}
}

function get_media_name(media_id) {
  for (let i = 0; i < media_data.length; i++) {
    var media = media_data[i];
    if (media['id'] == media_id) {
      return media['name'];
    }
  }
  return false;
COUCOU
}

function update_info(node, clicked_node_type) {

  let info = "";
  if (clicked_node_type == "story") {

    let story = null;
    for (let i = 0; i < stories_data.length; i++) {
      story = stories_data[i];
      if (story['story_id'] == node) {
        break;
      }
    }
    let media_name = get_media_name(story['media_id'])

    info = `<p><h3 id="titre">Story n°${story['story_id']}</h3></p>
            <p>${media_name} id: ${story['media_id']}</p>
            <p><a href=${story['url']} target=blank>Lien vers l'article.</a></p>`
    $("#info").html(info);
  }


  else if (clicked_node_type == "media") {
    let media = null;
    for (let i = 0; i < media_data.length; i++) {
      media = media_data[i];
      if (media['id'] == node) {
        break;
      }
    }
    info = `<p><h3 id="titre">Media: ${media['name']}</h3></p>
            <p>media_id: ${media['id']}</p>`
    $("#info").html(info);

  }

  else if (clicked_node_type == "baricenter") {

    let baricenter = null;
    for (let i = 0; i < baricenter_data.length; i++) {
      baricenter = baricenter_data[i];
      if (baricenter['quarter'] == node) {
        break;
      }
    }
    let position = get_position(node);
    info = `<p><h3 id="titre">Barycentre numéro ${baricenter['quarter']}</h3></p>
            <p>Coordonnées: x=${baricenter['x']}, y=${baricenter['y']}, z=${baricenter['z']}</p>
            <p>${position}</p>
            `
    $("#info").html(info);

  }
  else if (clicked_node_type == "update"){
    info = `<p><h3 id="titre">Bienvenu dans le monde des confettis</h3></p>
            <p><a href="https://github.com/medialab/peristyle">Lien vers le code source.</a></p>`

    $("#info").html(info);
  }


}


function create_graph_3D( dimension1, dimension2, dimension3, dimension3_signe, colors) {
  const graph = new UndirectedGraph();

  //Add baricenters nodes
  for (let i = 0; i < baricenter_data_3D.length; i++){
    let baricenter = baricenter_data_3D[i];
    if (dimension3_signe == 'positif' && baricenter[dimension3] > 0) {
      graph.addNode(baricenter['quarter'], {x:baricenter[dimension1], y:baricenter[dimension2], size:5, label:baricenter['quarter'], color:'#ff0080'});
      console.log(baricenter)
    }
    else if (dimension3_signe == 'negatif' && baricenter[dimension3] <= 0) {
      graph.addNode(baricenter['quarter'], {x:baricenter[dimension1], y:baricenter[dimension2], size:5, label:baricenter['quarter'], color:'#ff0080'});
    }
  }

  //Add stories nodes
  for (let i = 0; i < stories_data_3D.length; i++) {
    let story = stories_data_3D[i];
    let color = colors[story['media_id']];
    if (media_wanted_id === 0) {
      if (dimension3_signe == 'positif' && story[dimension3] > 0 ) {
        graph.addNode(story['story_id'], {x:story[dimension1], y:story[dimension2], size:1, label:story['story_id'], color:color});
      }
      else if (dimension3_signe == 'negatif' && story[dimension3] <= 0) {
        graph.addNode(story['story_id'], {x:story[dimension1], y:story[dimension2], size:1, label:story['story_id'], color:color});
      }
    }
    else {
      if (story['media_id'] == media_wanted_id) {
        if (dimension3_signe == 'positif' && story[dimension3] > 0 ) {
          graph.addNode(story['story_id'], {x:story[dimension1], y:story[dimension2], size:1, label:story['story_id'], color:highlight_color});
        }
        else if (dimension3_signe == 'negatif' && story[dimension3] <= 0) {
          graph.addNode(story['story_id'], {x:story[dimension1], y:story[dimension2], size:1, label:story['story_id'], color:highlight_color});
        }
      }
      else {
        if (dimension3_signe == 'positif' && story[dimension3] > 0 ) {
          graph.addNode(story['story_id'], {x:story[dimension1], y:story[dimension2], size:1, label:story['story_id'], color:transparent_color});
        }
        else if (dimension3_signe == 'negatif' && story[dimension3] <= 0) {
          graph.addNode(story['story_id'], {x:story[dimension1], y:story[dimension2], size:1, label:story['story_id'], color:transparent_color});
        }
      }
    }
  }

  //Add medias nodes
  for (let i = 0; i< media_data_3D.length; i++) {
    let media = media_data_3D[i];
    let color = colors[media['id']];
    if (media['id'] === media_wanted_id) {
      console.log(media)
      if (dimension3_signe == 'positif' && media[dimension3] > 0) {
        graph.addNode(media['id'], {x:media[dimension1], y:media[dimension2], size:6, label:media['name'], color:highlight_color});
        }
      else if (dimension3_signe == 'negatif' && media[dimension3] <= 0) {
        graph.addNode(media['id'], {x:media[dimension1], y:media[dimension2], size:6, label:media['name'], color:highlight_color});
        }
      }
    else {
      if (dimension3_signe == 'positif' && media[dimension3] > 0) {
        graph.addNode(media['id'], {x:media[dimension1], y:media[dimension2], size:3, label:media['name'], color:color});
        }
      else if (dimension3_signe == 'negatif' && media[dimension3] <= 0) {
        graph.addNode(media['id'], {x:media[dimension1], y:media[dimension2], size:3, label:media['name'], color:color});
        }
      }
    }
  return graph;
}

function create_graph_2D() {
  const graph = new UndirectedGraph();

  for (let i = 0; i < baricenter_data_2D.length; i++) {
    let baricenter = baricenter_data_2D[i];
    console.log(baricenter);
    graph.addNode(baricenter['quarter'], {x:baricenter['x'], y:baricenter['y'], size:5, label:baricenter['quarter'], color:'#ff0080'});
  }

  //Add stories nodes
  for (let i = 0; i < stories_data_2D.length; i++) {
    let story = stories_data_2D[i];
    let color = colors[story['media_id']];

    if (media_wanted_id === 0) {
        graph.addNode(story['story_id'], {x:story['x'], y:story['y'], size:1, label:story['story_id'], color:color});
    }
    else {
      if (story['media_id'] == media_wanted_id) {
        graph.addNode(story['story_id'], {x:story['x'], y:story['y'], size:1, label:story['story_id'], color:highlight_color});
      }
      else {
        graph.addNode(story['story_id'], {x:story['x'], y:story['y'], size:1, label:story['story_id'], color:transparent_color});
      }
    }
  }

  //Add medias nodes
  for (let i = 0; i< media_data_2D.length; i++) {
    let media = media_data_2D[i];
    let color = colors[media['id']];

    if (media['id'] === media_wanted_id) {
      graph.addNode(media['id'], {x:media["x"], y:media["y"], size:6, label:media['name'], color:highlight_color});
      }
    else {
      graph.addNode(media['id'], {x:media["x"], y:media["y"], size:3, label:media['name'], color:color});
      }
    }
  return graph;
}



const container = document.getElementById('container');

function create_renderer(graph, sources, colors) {
  const renderer = new WebGLRenderer(graph, container);

  // Highlight clicked nodes
  renderer.on('clickNode', ({node}) => {
    let clicked_node_type = get_node_type(node);

    // update the info box
    update_info(node, clicked_node_type);
    console.log(clicked_node_type);

    // Set the source
    let source = "";
    if (clicked_node_type != "baricenter") {
      if (clicked_node_type == "story") {
        media_wanted_id = sources[node];
      }
      else {
        media_wanted_id = node;
      }
    }
    console.log(colors);
    graph.nodes().forEach(function(n){
      let type_n = get_node_type(n);

      if (type_n == "story") {
        if (sources[n] != media_wanted_id) {
          graph.setNodeAttribute(n, 'color', transparent_color);
        }
        else {
          graph.setNodeAttribute(n, 'color', highlight_color);
        }
      }
      else if (type_n == "baricenter") {
        if (clicked_node_type == "baricenter") {
          graph.setNodeAttribute(n, 'color', highlight_color);
          graph.setNodeAttribute(n, 'size', 6);
        }
        else {
          graph.setNodeAttribute(n, 'color', baricenter_color);
          graph.setNodeAttribute(n, 'size', 5);
        }
      }
      else {
        if (n == media_wanted_id) {
          graph.setNodeAttribute(n, 'color', highlight_color);
          graph.setNodeAttribute(n, 'size', 6);
        }
        else {
          graph.setNodeAttribute(n, 'color', colors[n]);
          graph.setNodeAttribute(n, 'size', 3);
        }

      }
    });
    console.log("mes chers parents je vole");
    renderer.refresh();
  });

  // Cleaning the highlight
  renderer.on('clickStage', () => {
    media_wanted_id = 0;
    update_info("", "update");

    console.log("lancement du nettoyage");

    graph.nodes().forEach(function(n) {
      let type_n = get_node_type(n);

      if (type_n == "baricenter") {
        graph.setNodeAttribute(n, 'size', 5);
        graph.setNodeAttribute(n, 'color', baricenter_color);

      }
      else if (type_n == "media") {
        graph.setNodeAttribute(n, 'size', 3);
        graph.setNodeAttribute(n, 'color', colors[n]);
      }
      else {
        graph.setNodeAttribute(n, 'size', 1);
        graph.setNodeAttribute(n, 'color', colors[sources[n]]);
      }
    });
    console.log("fin du nettoyege");
    renderer.refresh();
    console.log("freg");
  });
  return renderer;

}


function create_renderer_specific(graph, sources, colors) {

  const renderer = new WebGLRenderer(graph, container);

  // Highlight clicked nodes
  renderer.on('clickNode', ({node}) => {
    let clicked_node_type = get_node_type(node);
    let clicked_node_media = 0;
    // update the info box
    update_info(node, clicked_node_type);

    // Set the source
    let source = "";
    if (clicked_node_type != "baricenter") {
      if (clicked_node_type == "story") {
        clicked_node_media = sources[node];
      }
      else {
        clicked_node_media = node;
      }
    }

    console.log(clicked_node_media);

    if (clicked_node_type === "media" ) {
      graph.setNodeAttribute(node ,'size', 5);
    }
    else if (clicked_node_type === "story" ) {
      graph.setNodeAttribute(node ,'size', 3);
    }

    graph.nodes().forEach(function(n){
      let type_n = get_node_type(n);

      if (type_n === "media") {
        if (n === clicked_node_media) {
          graph.setNodeAttribute(node ,'size', 5);
        }
        else if (n !== node && n !== media_wanted_id) {
          graph.setNodeAttribute(n, 'size', 3);
        }
      }
      else if (type_n === "story") {
        if (sources[n] === clicked_node_media) {
          graph.setNodeAttribute(n, 'color', colors[clicked_node_media]);
        }
        if (n !== node) {
          graph.setNodeAttribute(n, 'size', 1);
        }
      }
    });

    renderer.refresh();
  });

  renderer.on('clickStage', () => {

    update_info(media_wanted_id, "media");

    console.log("lancement du nettoyage");

    graph.nodes().forEach(function(n) {
      let type_n = get_node_type(n);

      if (type_n == "baricenter") {
        graph.setNodeAttribute(n, 'size', 5);
      }
      else if (type_n == "media" && n != media_wanted_id) {
          graph.setNodeAttribute(n, 'size', 3);
      }
      else if (type_n == "story") {
        graph.setNodeAttribute(n, 'size', 1);
        if (sources[n] !== media_wanted_id) {
          graph.setNodeAttribute(n, 'color', transparent_color);
        }
      }
    });
    console.log("fin du nettoyege");
    renderer.refresh();
    console.log("freg");
  });

  return renderer;

}

let baricenter_data_2D = null;
let media_data_2D = null;
let stories_data_2D = null;


let baricenter_data_3D = null;
let media_data_3D = null;
let stories_data_3D = null;
let renderer = null;

let baricenter_data = null;
let media_data = null;
let stories_data = null;

let sources = null;
let colors = null;
let nb_dimension = 3;



Promise.all([baricenter_promise_3D, media_promise_3D, stories_promise_3D, baricenter_promise_2D, media_promise_2D, stories_promise_2D])
.then( function(values) {
  baricenter_data_3D = values[0];
  media_data_3D = values[1];
  stories_data_3D = values[2];

  baricenter_data_2D = values[3];
  media_data_2D = values[4];
  stories_data_2D = values[5];

  baricenter_data = baricenter_data_3D;
  stories_data = stories_data_3D;
  media_data = media_data_3D;
  document.getElementById("reset_2D").hidden = true;
  document.getElementById("loader").hidden = true;

  renderer = update_graph_3D('y', 'x', 'z', 'positif');

  for (let i = 0; i < media_data.length; i++) {
    var media = media_data[i];
    $("#media_wanted").append(new Option(media['name'], media['id']));
  }
})


function update_graph_3D(dimension1, dimension2, dimension3, dimension3_signe) {
  sources = set_sources(stories_data);
  colors = set_colors(media_data);

  if (renderer !== null) {
    renderer.kill();
  }

  let graph = create_graph_3D(dimension1, dimension2, dimension3, dimension3_signe, colors);

  if (specific_state === true) {
    renderer = create_renderer_specific(graph, sources, colors);
  }

  else {
    renderer = create_renderer(graph, sources, colors);
  }
  window.graph = graph;
  window.renderer = renderer;
  window.camera = renderer.camera;
  return renderer;
}

function update_graph_2D() {
  sources = set_sources(stories_data);
  colors = set_colors(media_data);

  renderer.kill();

  let graph =create_graph_2D();
  if (specific_state === true) {
    renderer = create_renderer_specific(graph, sources, colors);
  }

  else {
    renderer = create_renderer(graph, sources, colors);
  }

  window.graph = graph;
  window.renderer = renderer;
  window.camera = renderer.camera;
  return renderer;
}



function get_z(x, y) {
  let z = "";
  if ((x == "x" && y == "y") || (x == "y" && y == "x")){ z = "z"; }
  if ((x == "y" && y == "z") || (x == "z" && y == "y")){ z = "x"; }
  if ((x == "z" && y == "x") || (x == "x" && y == "z")){ z = "y"; }
  return z;
}

let i = 0;


$("#submit").on("click", function(e) {
  if (validite == true) {

      update_info("", "update");
      let x = $('input[name="X"]:checked').attr('value');
      let y = $('input[name="Y"]:checked').attr('value');
      let z = get_z(x ,y );
      let z_signe = $('input[name="Z"]:checked').attr('value');
      console.log(x, y, z, z_signe);
      renderer = update_graph_3D(x, y, z, z_signe, renderer);


  }
  else {
    let error = $("#submitError");
    error.text('Je répète : vous avez selectionner deux fois la même dimension (pas d\'affichage possible)');
  }
});

$('#reset_3D').on("click", function(e) {
  specific_state = false;
  media_wanted_id = 0;
  update_info("", "update");
  $("input[name='X'][value='x']").prop('checked', true);
  $("input[name='Y'][value='y']").prop('checked', true);
  $("input[name='Z'][value='positif']").prop('checked', true);
  $( "select#media_wanted" ).val(0);

  renderer = update_graph_3D("x", "y", "z", "positif");
});

$('#reset_2D').on("click", function(e) {
  specific_state = false;
  media_wanted_id = 0;
  update_info("", "update");
  $( "select#media_wanted" ).val(0);
  renderer = update_graph_2D();
});

$('#media_wanted').on("change", function(e){

  media_wanted_id = $( "select#media_wanted" ).val();
  update_info(media_wanted_id, "media");

  if (media_wanted_id != "");{
    specific_state = true;
    if (nb_dimension === 3) {
      let x = $('input[name="X"]:checked').attr('value');
      let y = $('input[name="Y"]:checked').attr('value');
      let z = get_z(x ,y );

      let z_signe = get_media_quarter(media_wanted_id, z);
      console.log(z_signe);
      $(`input[value=${z_signe}]`).prop('checked', true);
      renderer = update_graph_3D(x, y, z, z_signe);
    }
    else {
      renderer = update_graph_2D();
    }
  }
  console.log(media_wanted_id);
});

let parameters_option = null;

$('#change_dimension').on("click", function(e) {
  nb_dimension = +($('input[name="nb_dimension"]:checked').attr('value'));
  media_wanted_id = 0;
  $( "select#media_wanted" ).val(0);
  update_info("", "update");

  if (nb_dimension === 3) {
    console.log(parameters_option);
    document.getElementById("3D_options").hidden  = false;
    document.getElementById("reset_2D").hidden  = true;
    specific_state = false;
    media_wanted_id = 0;
    update_info("", "update");
    $("input[name='X'][value='x']").prop('checked', true);
    $("input[name='Y'][value='y']").prop('checked', true);
    $("input[name='Z'][value='positif']").prop('checked', true);
    $( "select#media_wanted" ).val(0);

    renderer = update_graph_3D("x", "y", "z", "positif");

  }
  else {

    baricenter_data = baricenter_data_2D;
    stories_data = stories_data_2D;
    media_data = media_data_2D;

    renderer = update_graph_2D();
    document.getElementById("3D_options").hidden  = true;
    document.getElementById("reset_2D").hidden  = false;

  }
});
