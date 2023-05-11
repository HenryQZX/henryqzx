var controls;
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
var innerColor = 0xff0000,
    outerColor = 0xff9900;
var innerSize = 25,
    outerSize = 30;

var renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setClearColor( 0x000000, 0 ); // background

renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// controls = new THREE.TrackballControls( camera );
// controls.noPan = true;
// controls.minDistance = 120;
// controls.maxDistance = 650;
//var width = window.innerWidth,
//    height = window.innerHeight / 2;
//var size = 128;
//var canvas = document.getElementById('canvasEl');
//    ctx = canvas.getContext('2d');
//
//function changeCanvas() {
//    ctx.font = '20pt Arial';
//    ctx.fillStyle = 'rgba(100,100,100,.1)';
//    ctx.fillRect(0, 0, canvas.width, canvas.height);
//    ctx.fillStyle = 'white';
//    //ctx.fillRect(10, 10, canvas.width - 20, canvas.height - 20);
//    ctx.fillStyle = 'orange';
//    ctx.textAlign = "center";
//    ctx.textBaseline = "middle";
//    ctx.fillText("踏得网", canvas.width / 2, canvas.height / 2 - 12);
//    ctx.fillStyle = 'red';
//    ctx.fillRect(20, canvas.height / 2 + 3, canvas.width - 40, 1);
//    ctx.font = '12pt Serif';
//    ctx.fillStyle = '#eee';
//    ctx.fillText("techbrood.com", canvas.width / 2, canvas.height / 2 + 12);
//}


camera.position.z = -400;
// Mesh
var group = new THREE.Group();
scene.add(group);

// Lights
var light = new THREE.AmbientLight( 0x404040 ); // soft white light
scene.add( light );

var directionalLight = new THREE.DirectionalLight( 0xffffff, 1 );
directionalLight.position.set( 0, 128, 128 );
scene.add( directionalLight );

// Sphere Wireframe Inner
var sphereWireframeInner = new THREE.Mesh(
  new THREE.IcosahedronGeometry( innerSize, 2 ),
  new THREE.MeshLambertMaterial({ 
    color: innerColor,
    ambient: innerColor,
    wireframe: true,
    transparent: true, 
    //alphaMap: THREE.ImageUtils.loadTexture( 'javascripts/alphamap.jpg' ),
    shininess: 0
  })
);
scene.add(sphereWireframeInner);

// Sphere Wireframe Outer
var sphereWireframeOuter = new THREE.Mesh(
  new THREE.IcosahedronGeometry( outerSize, 3 ),
  new THREE.MeshLambertMaterial({ 
    color: outerColor,
    ambient: outerColor,
    wireframe: true,
    transparent: true,
    alphaMap: THREE.ImageUtils.loadTexture( 'js/logo.png' ),
    shininess: 0 
  })
);
scene.add(sphereWireframeOuter);


// Sphere Glass Inner
var sphereGlassInner = new THREE.Mesh(
  new THREE.SphereGeometry( innerSize, 32, 32 ),
  new THREE.MeshPhongMaterial({ 
    color: innerColor,
    ambient: innerColor,
    transparent: true,
    shininess: 25,
    alphaMap: THREE.ImageUtils.loadTexture( 'js/logo.png' ),
    opacity: 0.3,
  })
);
scene.add(sphereGlassInner);

// Sphere Glass Outer
var sphereGlassOuter = new THREE.Mesh(
  new THREE.SphereGeometry( outerSize, 32, 32 ),
  new THREE.MeshPhongMaterial({ 
    color: outerColor,
    ambient: outerColor,
    transparent: true,
    shininess: 25,
    alphaMap: THREE.ImageUtils.loadTexture( 'js/logo.png' ),
    opacity: 0.3,
  })
);
scene.add(sphereGlassOuter);
//var manager = new THREE.LoadingManager();
//var loader=new THREE.FontLoader();//开始创建文字
//loader.load("droid_sans_regular.typeface.json", function(font){
//    //上面导入了optimer_regular.typeface.json
//	var new_text=new THREE.TextGeometry("text you want to show", {
//		font:font,
//		size:0.5,
//		height:0.3,
//		/*
//		这里只定义了最基本的参数
//		还有其他的参数
//		font: THREE.Font的实例
//		size: Float, 字体大小, 默认值为100
//		height: Float, 挤出文本的厚度。默认值为50
//		curveSegments: Integer, (表示文本的)曲线上点的数量，默认值为12
//		bevelEnabled: Boolean, 是否开启斜角，默认为false
//		bevelThickness: Float, 文本上斜角的深度，默认值为20
//		bevelSize: Float, 斜角与原始文本轮廓之间的延伸距离, 默认值为8
//		bevelSegments: Integer, 斜角的分段数, 默认值为3
//		*/
//	});
//	var material_text=new THREE.MeshLambertMaterial({color:0x9933FF});
//	/*
//	定义可以反光的材料,
//	也可以使用MeshBasicMeterial,
//	只是对光源无效
//	0x9933FF是十六进制颜色名
//	*/
//	var text_1=new THREE.Mesh(new_text, material_text);
//	//创建文字
//	scene.add(text_1);
//	//添加文字
//	text_1.position.z=-7.4;
//	text_1.position.y=4;
//	text_1.position.x=-2.5;
//});

// Particles Outer
var geometry = new THREE.Geometry();
for (i = 0; i < 35000; i++) {
  
  var x = -1 + Math.random() * 2;
  var y = -1 + Math.random() * 2;
  var z = -1 + Math.random() * 2;
  var d = 1 / Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2) + Math.pow(z, 2));
  x *= d;
  y *= d;
  z *= d;
   
  var vertex = new THREE.Vector3(
         x * outerSize,
         y * outerSize,
         z * outerSize
  );
   
  geometry.vertices.push(vertex);

}


var particlesOuter = new THREE.PointCloud(geometry, new THREE.PointCloudMaterial({
  size: 0.1,
  color: outerColor,
  //map: THREE.ImageUtils.loadTexture( 'javascripts/particletextureshaded.png' ),
  transparent: true,
  })
);
scene.add(particlesOuter);

// Particles Inner
var geometry = new THREE.Geometry();
for (i = 0; i < 35000; i++) {
  
  var x = -1 + Math.random() * 2;
  var y = -1 + Math.random() * 2;
  var z = -1 + Math.random() * 2;
  var d = 1 / Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2) + Math.pow(z, 2));
  x *= d;
  y *= d;
  z *= d;
   
  var vertex = new THREE.Vector3(
         x * outerSize,
         y * outerSize,
         z * outerSize
  );
   
  geometry.vertices.push(vertex);

}


var particlesInner = new THREE.PointCloud(geometry, new THREE.PointCloudMaterial({
  size: 0.1,
  color: innerColor,
  //map: THREE.ImageUtils.loadTexture( 'javascripts/particletextureshaded.png' ),
  transparent: true,
  })
);
scene.add(particlesInner);

// Starfield
var geometry = new THREE.Geometry();
for (i = 0; i < 5000; i++) {
  var vertex = new THREE.Vector3();
  vertex.x = Math.random()*2000-1000;
  vertex.y = Math.random()*2000-1000;
  vertex.z = Math.random()*2000-1000;
  geometry.vertices.push(vertex);
}
var starField = new THREE.PointCloud(geometry, new THREE.PointCloudMaterial({
  size: 2,
  color: 0xffff99
  })
);
scene.add(starField);


camera.position.z = -110;
//camera.position.x = mouseX * 0.05;
//camera.position.y = -mouseY * 0.05;
//camera.lookAt(scene.position);

var time = new THREE.Clock();

var render = function () {  
  //camera.position.x = mouseX * 0.05;
  //camera.position.y = -mouseY * 0.05;
  camera.lookAt(scene.position);

  sphereWireframeInner.rotation.x += 0.002;
  sphereWireframeInner.rotation.z += 0.002;
  
  sphereWireframeOuter.rotation.x += 0.001;
  sphereWireframeOuter.rotation.z += 0.001;
  
  sphereGlassInner.rotation.y += 0.005;
  sphereGlassInner.rotation.z += 0.005;

  sphereGlassOuter.rotation.y += 0.01;
  sphereGlassOuter.rotation.z += 0.01;

  particlesOuter.rotation.y += 0.0005;
  particlesInner.rotation.y -= 0.002;
  
  starField.rotation.y -= 0.002;

  var innerShift = Math.abs(Math.cos(( (time.getElapsedTime()+2.5) / 20)));
  var outerShift = Math.abs(Math.cos(( (time.getElapsedTime()+5) / 10)));

  starField.material.color.setHSL(Math.abs(Math.cos((time.getElapsedTime() / 10))), 1, 0.5);

  sphereWireframeOuter.material.color.setHSL(0, 1, outerShift);
  sphereGlassOuter.material.color.setHSL(0, 1, outerShift);
  particlesOuter.material.color.setHSL(0, 1, outerShift);

  sphereWireframeInner.material.color.setHSL(0.08, 1, innerShift);
  particlesInner.material.color.setHSL(0.08, 1, innerShift);
  sphereGlassInner.material.color.setHSL(0.08, 1, innerShift);

  sphereWireframeInner.material.opacity = Math.abs(Math.cos((time.getElapsedTime()+0.5)/0.9)*0.5);
  sphereWireframeOuter.material.opacity = Math.abs(Math.cos(time.getElapsedTime()/0.9)*0.5);


  directionalLight.position.x = Math.cos(time.getElapsedTime()/0.5)*128;
  directionalLight.position.y = Math.cos(time.getElapsedTime()/0.5)*128;
  directionalLight.position.z = Math.sin(time.getElapsedTime()/0.5)*128;

  // controls.update();

  renderer.render(scene, camera);
  requestAnimationFrame(render);  
};
//changeCanvas();
render();



// Mouse and resize events
document.addEventListener( 'mousemove', onDocumentMouseMove, false );
window.addEventListener('resize', onWindowResize, false);

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function onDocumentMouseMove( event ) {
  mouseX = event.clientX - window.innerWidth/2;
  mouseY = event.clientY - window.innerHeight/2;
}
